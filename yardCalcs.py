import random
from enum import Enum
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls

np.set_printoptions(precision=2, suppress=True) 

dbgLocal = 1          
class ydCalcs():
    
    def __init__(self):
        self.bldConsist = {}
        self.actionList = ["brkDnTrn", "swTrain", "buildTrain", "servIndus", "misc"]
        #self.weights = [0.18, 0.18, 0.18, 0.18, 0.1]
        self.weights = [0.3, 0.3, 0.3, 0, 0.1]
        #self.weights = [0, 0, 0, 0, 0]
        from locProc import locProc
        self.locProcObj = locProc()
        from classCars import classCars
        self.classObj = classCars()
        from display import dispItems
        self.dispObj = dispItems()
        
        self.startMisc = 0
        self.ready2Pickup = 0

    class Action_e(Enum):
        BRKDNTRN     = 0
        SWTRAIN      = 1
        BUILDTRAIN   = 2
        SERVINDUS    = 3
        MISC         = 4

    def setWeights(self, loc):
        action_e = ydCalcs.Action_e
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
        
    def randomTrack(self):
        return ''.join(random.choice(self.thisLocDests))


    def yardMaster(self, thisLoc, loc):
        self.setWeights(loc)
        choice = random.choices(self.actionList, weights=self.weights, k=1)
        choice = ''.join(choice)
        if mVars.prms["dbgYdProc"]: print("\nchoice: ", choice)
        
        self.dispObj.dispLocDat(loc)
        if self.startMisc:
            while self.startMisc < endMisc:
                self.startMisc +=1
            self.startMisc = 0

        match choice:
            case "brkDnTrn":
                self.brkDownTrain(loc)
            case "swTrain":
                if trainDB.ydTrains["swTrain"]:
                    self.swTrain(loc)
                    pass
            case "buildTrain":
                self.buildTrain(loc)
                pass
            case "servIndus":
                pass
            case "misc":
                self.startMisc = mVars.time
                endMisc = self.startMisc + mVars.prms["miscWaitTime"]
                pass

    def brkDownTrain(self, loc):
        if trainDB.ydTrains["brkDnTrn"]:
            ydTrainNam = random.choice(trainDB.ydTrains.get("brkDnTrn"))
            print("ydtrainNam: ", ydTrainNam)
            self.dispObj.dispActionDat(loc, "brkDnTrn", ydTrainNam)

            availCars = self.classObj.train2Track(loc, ydTrainNam)
            if availCars == 0:
                # train no longer has cars
                # remove train name from trainDB.ydTrains and locs.locData
                self.locProcObj.rmTrnFromLoc("brkDnTrn", loc, ydTrainNam)
                trainDB.trains.pop(ydTrainNam)
        if mVars.prms["dbgYdProc"]: 
            #if dbgLocal: print("after brkDnTrn: consist: ", 
            #self.thisConsist)
            #if dbgLocal: print("this location trackTots: ", locs.locDat[loc]["trackTots"])
            pass


        
    def buildTrain(self, loc):
        #if mVars.prms["dbgYdProc"]: print("buildTrain: number of cars available: ", numCarsAvail)
        
        # yard has no train undergoing build
        if not trainDB.ydTrains["buildTrain"]:
            
            self.buildNewTrain(loc)
            
            
        # yard has a train already building; add cars to it
        # single train is allowed to build in a yard
        else:    
            ydTrainNam = ''.join(trainDB.ydTrains["buildTrain"])     
            availCars, trainDest = self.classObj.track2Train(loc, ydTrainNam)
            trainStem = trainDB.trains[ydTrainNam]

            if trainStem["numCars"] >= mVars.prms["trainSize"]*0.7:
                # train has reached max size
                self.locProcObj.startTrain("buildTrain", loc, ydTrainNam)

    def ready2Build(self, loc):
        trackList = [trackTot for trackTot in locs.locDat[loc]["trackTots"] if "indust" not in trackTot]
        maxCars = max(trackList)
        trackMaxCars = trackList[trackList.index(maxCars)]

        if locs.locDat[loc]["trackTots"][trackMaxCars] >= mVars.prms["trainSize"]*0.5: return trackMaxCars
        else: return 0
        
        
                            
    def buildNewTrain(self, loc):
        from trainProc import trainParams

        trackMaxCars = self.ready2Build(loc)
        if trackMaxCars:            
            trainObj = trainParams()
            trnName, conName = trainObj.newTrain()

            trainDB.trains[trnName].update( {
                "status": "building",
                "origLoc": loc,
                "nextLoc": trackMaxCars,
                "currentLoc": loc,
                "numStops": 1,
                "stops": {trackMaxCars: {"action": "terminate"}},
                "color": trainParams.colors()           
                    })
            trainDB.consists[conName].update({
                "stops": {trackMaxCars:{"box": 0, "tank": 0,"rfr": 0, "hop": 0, 
                "gons": 0, "flats": 0, "psgr": 0}  }
            })
            
            print("new train: ", trnName, ": ", trainDB.trains[trnName])
            print("new consist: ", conName, ":", trainDB.consists[conName])
            trainDB.ydTrains["buildTrain"].append(trnName)
            locs.locDat[loc]["trains"].append(trnName)
            return

    
            
    def swTrain(self, loc):
        # remove cars from train and save on tracks
        # until all cars removed for this stop 
        
        # find out what train is being switched or add new one
        locStem = locs.locDat[loc]["trn4Action"]
        if "swTrain"not in locStem:
            # no trains are undergoing swTrain
            ydTrainNam = random.choice(trainDB.ydTrains.get("swTrain"))
            locStem.append({"swTrain": ydTrainNam})
        else:
            ydTrainNam = locStem["swTrain"]
            
        print("ydtrainNam: ", ydTrainNam)
        self.dispObj.dispActionDat(loc, "swTrain", ydTrainNam)

        if self.ready2Pickup == 0:
            availCars = self.classObj.train2Track(loc, ydTrainNam)
            if availCars == 0:
                trainStem = trainDB.trains[ydTrainNam]
                trainStem["stops"].pop(loc)
                consistNum = trainStem["consistNum"]
                consistNam = "consist"+str(consistNum)
                trainDB.consists[consistNam]["stops"].pop(loc)
                if mVars.prms["dbgYdProc"]: print("swTrain: train:", ydTrainNam, 
                    " trainDict: ", trainStem)
                self.ready2Pickup = 1
        # add cars to train until train is max size
        if self.ready2Pickup:
            availCars, trainDest = self.classObj.track2Train(loc, ydTrainNam)
            if trainDB.trains[ydTrainNam]["numCars"] >= mVars.prms["trainSize"]*1.2:
                # train has reached max size
                # train no longer has pickups or drops
                # start train to nextLoc, if there are more stops and
                # remove train name from locs.locData
                self.locProcObj.startTrain("swTrain", loc, ydTrainNam)
        
        pass
    def servIndus(self):
        pass
    # calc trains that arrive, trains ready to leave (and do they?)
    # cars classified; need a dict with all car types, next dest (track or 
    # loc), status (ready to classify, classified, in arriving train)
        #self.trainOut = self.rateClassification*self.fracTrainBuild/mVars.trainSize


