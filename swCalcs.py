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
        ROADCREWSW   = 1
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
        trainDB.ydTrains = {"dropPickup": [], "roadCrewSw": [], "ready2Leave": [], "turn": []}

        # train status leads to actions by the yard crew or
        # the train crew.  Train actions are the same name as
        # the corresponding train status string
        for trainNam in locs.locDat[loc]["trains"]:
            match trainDB.trains[trainNam]["status"]:
                case "dropPickup":
                    if trainNam not in trainDB.ydTrains["dropPickup"]:
                        trainDB.ydTrains["dropPickup"].append(trainNam)
                case "roadCrewSw":
                    if trainNam not in trainDB.ydTrains["roadCrewSw"]:
                        trainDB.ydTrains["roadCrewSw"].append(trainNam)
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
        if len(trainDB.ydTrains["roadCrewSw"]) == 0: return
        
        locActionStem = locs.locDat[loc]["trn4Action"]
        found = [d for d in locActionStem if "roadCrewSw" in d]
        if not found:
            # no trains are undergoing swTrain
            ydTrainNam = random.choice(trainDB.ydTrains.get("roadCrewSw"))
            locActionStem.append({"roadCrewSw": ydTrainNam})
        else:
            entry = next(iter(locActionStem))
            ydTrainNam = entry["roadCrewSw"]
            # same train continues to switch industries, 
            # starting with the same industry stored in last time step
            
        found = [d for d in locActionStem if "industry" in d]
        if found: industry = locActionStem["industry"]
        else:
            industry = next(iter(locs.locDat[loc]["industries"]))
            print("industry: ", industry)
            
        print("ydtrainNam: ", ydTrainNam, ", industry: ", industry, ", nextSwStep: ", swCalcs.nextSwStep,
              ", trn4Action: ", locs.locDat[loc]["trn4Action"])
        
        self.swIndus(loc, ydTrainNam, industry)
        return
        
            
    def swIndus(self, loc, ydTrainNam, indus):
            
        self.dispObj.dispActionDat(loc, "swTrain", ydTrainNam)

        consistNam = trainDB.getConNam(ydTrainNam)
        # add pickups to train
        if swCalcs.nextSwStep == 0:
            thisTrack = locs.locDat[loc]["industries"][indus]["pickups"]
            availCars = self.classObj.track2Train(loc, thisTrack, ydTrainNam, consistNam)
            if availCars == 0:
                locs.locDat[loc]["industries"][indus].pop("pickups")
                swCalcs.nextSwStep = 1
                #removes this train from "trn4Action"
                locs.locDat[loc]["trn4Action"] = [d for d in locs.locDat[loc]["trn4Action"] if "swTrain" not in d]
                if mVars.prms["dbgYdProc"]: print("trn4Action:", 
                        locs.locDat[loc]["trn4Action"])
                
        # remove cars from train and place on industry tracks
        # until all requested cars are spotted 
        else:
            thisTrack = locs.locDat[loc]["industries"][indus]["leave"]
            cars2Spot = locs.locDat[loc]["industries"]["spot"]
            availCars, trainDest = self.classObj.train2Track(loc, thisTrack, ydTrainNam, consistNam)
            if trainDB.trains[ydTrainNam]["numCars"] >= mVars.prms["trainSize"]*1.2:
                # train has reached max size
                # train no longer has pickups or drops
                # start train to nextLoc, if there are more stops and
                # remove train name from locs.locData
                trainStem = trainDB.trains[ydTrainNam]
                trainStem["stops"].pop(loc)
                consistNum = trainStem["consistNum"]
                consistNam = "consist"+str(consistNum)
                trainDB.consists[consistNam]["stops"].pop(loc)
                if mVars.prms["dbgYdProc"]: print("swTrain: train:", ydTrainNam, 
                    " trainDict: ", trainStem)

                self.locProcObj.startTrain("swTrain", loc, ydTrainNam)
        
        pass
    def servIndus(self, loc):
        pass
    # calc trains that arrive, trains ready to leave (and do they?)
    # cars classified; need a dict with all car types, next dest (track or 
    # loc), status (ready to classify, classified, in arriving train)
        #self.trainOut = self.rateClassification*self.fracTrainBuild/mVars.trainSize


