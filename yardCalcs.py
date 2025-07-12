import random
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from gui import gui

np.set_printoptions(precision=2, suppress=True) 

dbgLocal = 1          
class ydCalcs():
    
    def __init__(self):
        self.bldConsist = {}
        self.actionList = ["brkDnTrn", "swTrain", "buildTrain", "servIndus", "misc"]
        #self.weights = [0.18, 0.18, 0.18, 0.18, 0.1]
        self.weights = [0.3, 0.3, 0.3, 0, 0.1]
        #trainDB.ydTrains = {"brkDnTrn": [], "swTrain": [], "buildTrain": [], "roadCrewSw": []}
        from locProc import locProc
        self.locProcObj = locProc()
        from classCars import classCars
        self.classObj = classCars()

    def randomTrack(self):
        return ''.join(random.choice(self.thisLocDests))


    def yardMaster(self, thisLoc, loc):
        
        choice = random.choices(self.actionList, weights=self.weights, k=1)
        choice = ''.join(choice)
        if mVars.prms["dbgYdProc"]: print("\nchoice: ", choice)
        
        match choice:
            case "brkDnTrn":
                #self.brkDownTrain(loc)
                if trainDB.ydTrains["brkDnTrn"]:
                    self.classObj.train2Track(loc, "brkDnTrn")

                if mVars.prms["dbgYdProc"]: 
                    #if dbgLocal: print("after brkDnTrn: consist: ", 
                    #self.thisConsist)
                    #if dbgLocal: print("this location trackTots: ", locs.locDat[loc]["trackTots"])
                    pass
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
                waitIdx = 0
                while waitIdx < mVars.waitTime:
                    waitIdx +=1
                    pass


    def buildTrain(self, loc):
        numCarsAvail = 0
        #if mVars.prms["dbgYdProc"]: print("buildTrain: number of cars available: ", numCarsAvail)
        
        # yard has no train undergoing build
        if not trainDB.ydTrains["buildTrain"]:
            
            self.buildNewTrain(loc)
            
            
        # yard has a train already building; add cars to it
        # single train is allowed to build in a yard
        else:         
            self.classObj.track2Train(loc, "buildTrain")
            ydtrainNam =  ''.join(trainDB.ydTrains["buildTrain"])
            trainStem = trainDB.trains[ydtrainNam]

            if trainStem["numCars"] >= mVars.prms["trainSize"]*0.7:
                # train has reached max size
                self.locProcObj.startTrain(loc, ydtrainNam)


    def findRoutes(self, loc, ydtrainNam):
        for routeNam in routeCls.routes:
            loc = ''.join(loc)
            dest = ''.join(trainDB.trains[ydtrainNam]["nextLoc"])
            if dbgLocal: print("routNam: ", routeNam, " loc: ", loc, 
                " nextLoc: ", dest, "route: ", routeCls.routes[routeNam])
            if (loc in routeCls.routes[routeNam].values()) and \
                (dest in routeCls.routes[routeNam].values()):
                return routeNam

                            
    def buildNewTrain(self, loc):
        from trainProc import trainParams

        genExp = (trackTot for trackTot in locs.locDat[loc]["trackTots"] if "indust" not in trackTot)
        for trackTots in genExp:
            if locs.locDat[loc]["trackTots"][trackTots] >= mVars.prms["trainSize"]*0.5:
                trainObj = trainParams()
                trnName, conName = trainObj.newTrain()

                trainDB.trains[trnName].update( {
                    "status": "building",
                    "origLoc": loc,
                    "nextLoc": trackTots,
                    "currentLoc": loc,
                    "numStops": 1,
                    "stops": {trackTots: {"action": "terminate"}},
                    "color": trainParams.colors()           
                        })
                trainDB.consists[conName].update({
                    "stops": {trackTots:{"box": 0, "tank": 0,"rfr": 0, "hop": 0, 
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
        self.classObj.train2Track(loc, "swTrain")
        # add cars to train until train is
        # 70% or more of max size 
        self.classObj.track2Train(loc, "swTrain")
        pass
    def servIndus(self):
        pass
    # calc trains that arrive, trains ready to leave (and do they?)
    # cars classified; need a dict with all car types, next dest (track or 
    # loc), status (ready to classify, classified, in arriving train)
        #self.trainOut = self.rateClassification*self.fracTrainBuild/mVars.trainSize


