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
        from classCars import classCars
        self.classObj = classCars()
        from display import dispItems
        self.dispObj = dispItems()
        

    class Action_e(Enum):
        DROPPICKUP   = 0
        rdCrwSw   = 1
        READY2LEAVE  = 2
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
        trainDB.ydTrains = {"dropPickup": [], "rdCrwSw": [], "ready2Leave": [], "turn": []}

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
                case "ready2Leave":
                    if trainNam not in trainDB.ydTrains["ready2Leave"]:
                        trainDB.ydTrains["ready2Leave"].append(trainNam)
                case "turn":
                    if trainNam not in trainDB.ydTrains["turn"]:
                        trainDB.ydTrains["turn"].append(trainNam)
        

    def switchArea(self, thisLoc, loc):
        #self.setWeights(loc)
        #choice = random.choices(self.actionList, weights=self.weights, k=1)
        #choice = ''.join(choice)
        #if mVars.prms["dbgYdProc"]: print("\nchoice: ", choice)
        
        self.dispObj.dispTrnLocDat(loc)
        
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
        found = [d for d in locActionStem if "industry" in d]
        if len(index) != 0: 
            industry = locActionStem[index[0]]["industry"]
        else:
            try:
                industry = next(swCalcs.indusIter)
                locActionStem.append({"industry": industry})
            except:
                print("all industries have been switched")
                self.cleanup(loc, ydTrainNam)
                self.locProcObj.startTrain("rdCrwSw", loc, ydTrainNam)
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
        
    def cleanup(self, loc, ydTrainNam):
        locActionStem = locs.locDat[loc]["trn4Action"]            
        index = [i for i, d in enumerate(locActionStem)\
            if "rdCrwSw" in d]
        locActionStem.pop(index[0])
        trainStem = trainDB.trains[ydTrainNam]
        # remove stop from train
        trainStem["stops"].pop(loc)
        # remove stop from consist
        consistNam = trainDB.getConNam(ydTrainNam)
        trainDB.consists[consistNam]["stops"].pop(loc)

