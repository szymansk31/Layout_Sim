import random
from enum import Enum
import numpy as np
from mainVars import mVars
from stateVars import locs, dspCh, trainDB, routeCls

np.set_printoptions(precision=2, suppress=True) 

dbgLocal = 1          
class ydCalcs():
    startMisc = 0
    ready2Pickup = 0

    def __init__(self):
        self.actionList = ["brkDnTrn", "buildTrain", "swTrain", "servIndus", "misc"]
        #self.weights = [0.18, 0.18, 0.18, 0.18, 0.1]
        self.weights = [0.33, 0.33, 0.33, 0, 0]
        #self.weights = [0, 0, 0, 0, 0]
        from locProc import locProc, locBase
        self.locProcObj = locProc()
        self.locBaseObj = locBase()
        from classCars import classCars
        self.classObj = classCars()
        from display import dispItems
        self.dispObj = dispItems()
        

    class Action_e(Enum):
        BRKDNTRN     = 0
        BUILDTRAIN   = 1
        SWTRAIN      = 2
        SERVINDUS    = 3
        MISC         = 4

    def setWeights(self):
        action_e = ydCalcs.Action_e
        totTrains = 0
        numTrains = {}
        weightPortion = 1 - self.weights[action_e.SERVINDUS.value] - self.weights[action_e.MISC.value]

        for action in trainDB.ydTrains:
            numTrains.update(
                {action: len(trainDB.ydTrains[action])
                })
        """
        Decision about building a train now determined by schedule
        # if a track has enough cars to build a train, then that increases weight of buildTrain
        numCars, maxCarTrk = self.ready2Build(loc)
        if (numCars>0) and (numTrains["buildTrain"] == 0): numTrains["buildTrain"] = 1
        """
        totTrains = sum(numTrains[action] for action in numTrains)
        idx = 0
        print("numTrains list, totTrains: ", numTrains, ",", totTrains)
        if totTrains != 0:
            for action in trainDB.ydTrains:
                self.weights[idx] = numTrains[action]/totTrains*weightPortion
                idx +=1
        if mVars.prms["dbgYdProc"]: print("action weights are: ", self.weights)
        return totTrains
        
    def cars2Class(self, loc):
        cars2Class = 0
        for train in trainDB.ydTrains["brkDnTrn"]:
            cars2Class += trainDB.trains[train]["numCars"]
        for train in trainDB.ydTrains["buildTrain"]: 
            cars2Class += mVars.prms["trainSize"] - \
                trainDB.trains[train]["numCars"]
        if "indust" in locs.locDat[loc]["destTrkTots"]:
            cars2Class += locs.locDat[loc]["destTrkTots"]["industries"]
        if locs.locDat[loc]["type"] == "swArea": 
            cars2Class += locs.locDat[loc]["numOffspot"]
        locs.locDat[loc]["cars2Class"] = cars2Class

    def yardMaster(self, loc):
        totTrains = self.setWeights()
        if totTrains == 0: 
            print("\nLocation: ", loc, " no trains to classify")
            return
        choice = random.choices(self.actionList, weights=self.weights, k=1)
        choice = ''.join(choice)
        if trainDB.ydTrains["swTrain"]: choice = "swTrain"  #always first priority
        if mVars.prms["dbgYdProc"]: print("\nchoice: ", choice)
        
        if locs.locDat[loc]["startMisc"]:
            while locs.locDat[loc]["startMisc"] < endMisc:
                locs.locDat[loc]["startMisc"] +=1
            locs.locDat[loc]["startMisc"] = 0

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
                self.servIndus(loc)
                pass
            case "misc":
                locs.locDat[loc]["startMisc"] = mVars.time
                endMisc = locs.locDat[loc]["startMisc"] + mVars.prms["miscWaitTime"]
                pass
        self.cars2Class(loc)
        self.dispObj.dispTrnLocDat(loc)
        

    def brkDownTrain(self, loc):
        if trainDB.ydTrains["brkDnTrn"]:
            ydTrainNam = random.choice(trainDB.ydTrains.get("brkDnTrn"))
            print("ydtrainNam: ", ydTrainNam)
            self.dispObj.dispActionDat(loc, "brkDnTrn", ydTrainNam)

            availCars = self.classObj.train2Track(loc, ydTrainNam)
            if availCars == 0:
                # train no longer has cars
                # remove train name from trainDB.ydTrains and locs.locData
                locs.locDat[loc]["trnCnts"]["brkDown"] += 1
                self.locBaseObj.rmTrnFrmActions("brkDnTrn", loc, ydTrainNam)
                self.locBaseObj.rmTrnFrmLoc(loc, ydTrainNam)
                trainDB.trains.pop(ydTrainNam)

        if mVars.prms["dbgYdProc"]: 
            #if dbgLocal: print("after brkDnTrn: consist: ", 
            #self.thisConsist)
            #if dbgLocal: print("this location destTrkTots: ", locs.locDat[loc]["destTrkTots"])
            pass

        
    def buildTrain(self, loc):   
        from trainInit import trainInit
        trainInitObj = trainInit() 
        ydTrainNam = trainDB.ydTrains["buildTrain"][0]
        # yard has no train undergoing build
        if trainDB.trains[ydTrainNam]["status"] == "init":
            #trainInitObj.fillTrnDicts(loc, ydTrainNam)
            trainDB.trains[ydTrainNam]["status"] = "building"
        else:
            # yard has a train already building; add cars to it
            # single train is allowed to build in a yard
            # dummy input is "indus" 
            availCars, trainDest = self.classObj.track2Train(loc, "", ydTrainNam)
            trainStem = trainDB.trains[ydTrainNam]
            self.dispObj.dispActionDat(loc, "buildTrain", ydTrainNam)

            if trainStem["numCars"] >= mVars.prms["trainSize"]*0.7:
                # train has reached max size
                trainStem["status"] = "built"
                locs.locDat[loc]["trnCnts"]["built"] += 1

                #self.locProcObj.startTrain("buildTrain", loc, ydTrainNam)

    def ready2Build(self, loc):
        import copy
        trackList = copy.deepcopy(locs.locDat[loc]["destTrkTots"])
        try:
            trackList.pop("industries")
        except:
            pass
        
        maxCarTrk = max(trackList, key=trackList.get)

        print("ready2Build: maxCarTrk: ", maxCarTrk, ", trackList: ", trackList)
        if locs.locDat[loc]["destTrkTots"][maxCarTrk] >= mVars.prms["trainSize"]*0.5:
            return trackList[maxCarTrk], maxCarTrk
        else: return 0,""
        
            
    def swTrain(self, loc):
        # remove cars from train and save on tracks
        # until all cars removed for this stop 
        
        # find out what train is being switched or add new one
        locStem = locs.locDat[loc]["trn4Action"]
        found = [d for d in locStem if "swTrain" in d]
        if not found:
            # no trains are undergoing swTrain
            ydTrainNam = random.choice(trainDB.ydTrains.get("swTrain"))
            locStem.append({"swTrain": ydTrainNam})
        else:
            entry = next(iter(locStem))
            ydTrainNam = entry["swTrain"]
            
        print("ydtrainNam: ", ydTrainNam, "ready2Pickup: ", ydCalcs.ready2Pickup,
              "trn4Action: ", locs.locDat[loc]["trn4Action"])
        self.dispObj.dispActionDat(loc, "swTrain", ydTrainNam)

        if ydCalcs.ready2Pickup == 0:
            availCars = self.classObj.train2Track(loc, ydTrainNam)
            if availCars == 0:
                trainStem = trainDB.trains[ydTrainNam]
                trainStem["stops"].pop(loc)
                consistNum = trainStem["consistNum"]
                consistNam = "consist"+str(consistNum)
                trainDB.consists[consistNam]["stops"].pop(loc)
                if mVars.prms["dbgYdProc"]: print("swTrain: train:", ydTrainNam, 
                    " trainDict: ", trainStem)
                ydCalcs.ready2Pickup = 1
        # add cars to train until train is max size
        else:
            availCars, trainDest = self.classObj.track2Train(loc, "", ydTrainNam)
            if trainDB.trains[ydTrainNam]["numCars"] >= mVars.prms["trainSize"]*1.2:
                # train has reached max size
                # train no longer has pickups or drops
                # start train to nextLoc, if there are more stops and
                # remove train name from locs.locData
                locs.locDat[loc]["trnCnts"]["switched"] += 1
                locs.locDat[loc]["trn4Action"] = [d for d in locStem if "swTrain" not in d]
                if mVars.prms["dbgYdProc"]: print("trn4Action:", 
                        locs.locDat[loc]["trn4Action"])
                self.locBaseObj.rmTrnFrmActions("swTrain", loc, ydTrainNam)
                self.locProcObj.startTrain(loc, ydTrainNam)
        
        pass
    def servIndus(self, loc):
        pass
