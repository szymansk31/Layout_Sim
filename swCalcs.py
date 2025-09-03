import random
from enum import Enum
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls

np.set_printoptions(precision=2, suppress=True) 

dbgLocal = 1          
class swCalcs():
    startMisc = 0
    nextSwStep = 0
    indusIter = any

    def __init__(self):
        #self.weights = [0.18, 0.18, 0.18, 0.18, 0.1]
        self.weights = [0.3, 0.3, 0.3, 0, 0]
        #self.weights = [0, 0, 0, 0, 0]
        from locProc import locProc
        self.locProcObj = locProc()
        from locBase import locBase, Qmgmt, locMgmt
        self.locBaseObj = locBase()
        self.locQmgmtObj = Qmgmt()
        self.locMgmtObj = locMgmt
        from classCars import classCars
        self.classObj = classCars()
        from display import dispItems
        self.dispObj = dispItems()
        from routeProc import rtCaps
        self.rtCapsObj = rtCaps()
        

    class Action_e(Enum):
        DROPPICKUP   = 0
        rdCrwSw   = 1
        wait4Clrnce  = 2
        TURN         = 3
        MISC         = 4

    def setWeights(self, loc):
        action_e = swCalcs.Action_e
        totTrains = 0
        numTrains = {}
        weightPortion = 1 - self.weights[action_e.SERVINDUS.value] - self.weights[action_e.MISC.value]

        for action in trainDB.ydTrains:
            numTrains.update(
                {action: len(trainDB.ydTrains[action])
                })
        # if a track has enough cars to build a train, then that increases weight of buildTrain
        if self.ready2Build(loc) and (numTrains["buildTrain"] == 0): numTrains["buildTrain"] +=1
        totTrains = sum(numTrains[action] for action in numTrains)
        idx = 0
        print("numTrains list, totTrains: ", numTrains, ",", totTrains)
        if totTrains != 0:
            for action in trainDB.ydTrains:
                self.weights[idx] = numTrains[action]/totTrains*weightPortion
                idx +=1
        if mVars.prms["dbgYdProc"]: print("action weights are: ", self.weights)
        
    def swAnalyzeTrains(self, loc):
        trainDB.ydTrains = {"dropPickup": [], "rdCrwSw": [], "wait4Clrnce": [], "turn": []}

        # train status leads to actions by the yard crew or
        # the train crew.  Train actions are the same name as
        # the corresponding train status string
        for trainNam in locs.locDat[loc]["trains"]:
            match trainDB.trains[trainNam]["status"]:
                case "dropPickup":
                    if trainNam not in trainDB.ydTrains["dropPickup"]:
                        trainDB.ydTrains["dropPickup"].append(trainNam)
                case "rdCrwSw":
                    if trainNam not in trainDB.ydTrains["rdCrwSw"]:
                        trainDB.ydTrains["rdCrwSw"].append(trainNam)
                case "wait4Clrnce":
                    if trainNam not in trainDB.ydTrains["wait4Clrnce"]:
                        trainDB.ydTrains["wait4Clrnce"].append(trainNam)
                case "continue":
                    # May have a call to 
                    # dispatcher eventually, so process "continue" here 
                    # as no action needed by train crew (modulo dispatch call)
                    if trainNam not in trainDB.ydTrains["continue"]:
                        trainDB.ydTrains["continue"].append(trainNam)
                    # train never entered ydTrains, so no need to remove
                    self.locProcObj.startTrain(loc, trainNam)
        
    def switchCalcs(self, loc):
        self.dispObj.dispTrnLocDat(loc)
        # assume two operators can work at the same time, if one is
        # switching industries and the other is dropping off
        trainsWorking = 0
        for action in ["dropPickup", "rdCrwSw"]:
            # allow up to two trains working at once
            
            if len(trainDB.ydTrains[action]) != 0:
                train = ''.join(trainDB.ydTrains[action])
                match action:
                    case "dropPickup":
                        self.dropPickup(loc, train)
                    case "rdCrwSw":
                        self.rdCrwSw(loc, train)
                pass
            trainsWorking +=1
            if trainsWorking == 2: return

    def dropPickup(self, loc, trainNam):
        # drop cars for this stop
        availCars = self.classObj.train2Track(loc, trainNam)
        if availCars == 0:
            # pickup cars earmarked for final location
            #availCars = self.classObj.track2Train(loc, trainNam)
            #if availCars == 0:
                # train no longer has cars
                # remove train name from trainDB.ydTrains and locs.locData
                self.locProcObj.startTrain(loc, trainNam)
                self.locMgmtObj.cleanupSwAction(loc, trainNam, "dropPickup")


    def rdCrwSw(self, loc, trainNam):
        # prepare for multiple trains in a swArea
        # first see if a train is already switching
        if len(trainDB.ydTrains["rdCrwSw"]) == 0: return
        
        
        locActionStem = locs.locDat[loc]["trn4Action"]
        index = [i for i, d in enumerate(locActionStem) if "rdCrwSw" in d]
        if len(index) == 0:
            # no trains are undergoing swTrain
            ydTrainNam = random.choice(trainDB.ydTrains.get("rdCrwSw"))
            locActionStem.append({"rdCrwSw": ydTrainNam})
        else:
            ydTrainNam = locActionStem[index[0]]["rdCrwSw"]
            # same train continues to switch industries, 
            # starting with the same industry stored in last time step
            
        index = [i for i, d in enumerate(locActionStem) if "industry" in d]
        if len(index) != 0: 
            industry = locActionStem[index[0]]["industry"]
        else:
            try:
                industry = next(swCalcs.indusIter)
                locActionStem.append({"industry": industry})
            except:
                print("all industries have been switched")
                self.locProcObj.startTrain(loc, ydTrainNam)
                self.locMgmtObj.cleanupSwAction(loc, ydTrainNam, "rdCrwSw")
                return

        print("industry: ", industry)
        print("ydtrainNam: ", ydTrainNam, ", industry: ", industry, ", nextSwStep: ", swCalcs.nextSwStep,
              ", trn4Action: ", locs.locDat[loc]["trn4Action"])
        
        self.swIndus(loc, ydTrainNam, industry)
        return
        
            
    def swIndus(self, loc, ydTrainNam, indus):
        locActionStem = locs.locDat[loc]["trn4Action"]            
        self.dispObj.dispSwitchDat(loc, indus, ydTrainNam)

        consistNam = trainDB.getConNam(ydTrainNam)
        # add pickups to train
        if swCalcs.nextSwStep == 0:
            availCars, trainDest = self.classObj.track2Train(loc, indus, ydTrainNam)
            if availCars == 0:
                #locs.locDat[loc]["industries"][indus].pop("pickups")
                swCalcs.nextSwStep = 1
                #removes this train from "trn4Action"
                #locs.locDat[loc]["trn4Action"] = [d for d in locs.locDat[loc]["trn4Action"] if "rdCrwSw" not in d]
                if mVars.prms["dbgYdProc"]: print("trn4Action:", 
                        locs.locDat[loc]["trn4Action"])
                
        # remove cars from train and place on industry tracks
        # until all requested cars are spotted 
        else:
            availCars, needCars, numNeedAA = self.classObj.train2Indus(loc, indus, ydTrainNam)
            if numNeedAA == 0:
                # car spotting finished at this industry
                index = [i for i, d in enumerate(locActionStem)\
                    if "industry" in d]
                locActionStem.pop(index[0])
                # move to next industry
                swCalcs.nextSwStep = 0
                self.dispObj.dispTrnLocDat(loc)
                
                if mVars.prms["dbgYdProc"]: print("swIndus: train:", ydTrainNam, 
                    " trainDict: ", trainDB.trains[ydTrainNam],
                    ", locAction: ", locActionStem)
        
