import random
import numpy as np
from mainVars import mVars
from trainProc import trainParams
from stateVars import locs, trainDB
from gui import gui
np.set_printoptions(precision=2, suppress=True) 

dbgLocal = 1          
class ydCalcs():
    
    def __init__(self):
        self.bldConsist = {}
        self.actionList = ["brkDnTrn", "swTrain", "buildTrain", "servIndus", "misc"]
        #self.weights = [0.18, 0.18, 0.18, 0.18, 0.1]
        self.weights = [0.45, 0, 0.45, 0, 0.1]
        self.ydTrains = {"brkDnTrn": [], "swTrain": [], "buildTrain": []}
        from locProc import locProc
        self.locProcObj = locProc()

    def randomTrack(self):
        return ''.join(random.choice(self.thisLocDests))


    def yardMaster(self, thisLoc, loc, ydTrainsIn):
        self.ydTrains = ydTrainsIn
        choice = random.choices(self.actionList, weights=self.weights, k=1)
        choice = ''.join(choice)
        if mVars.prms["dbgYdProc"]: print("\nchoice: ", choice)
        
        match choice:
            case "brkDnTrn":
                self.brkDownTrain(loc)
                if mVars.prms["dbgYdProc"]: 
                    #if dbgLocal: print("after brkDnTrn: consist: ", 
                    #self.thisConsist)
                    #if dbgLocal: print("this location trackTots: ", locs.locDat[loc]["trackTots"])
                    pass
            case "swTrain":
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

    def brkDownTrain(self, loc):
        from carProc import carProc
        carProcObj = carProc()
        rate = mVars.geometry[loc]["classRate"]
        self.thisLocDests = self.locProcObj.locDests(loc)

        for ydtrainNam in self.ydTrains["brkDnTrn"]:
            consistNum = trainDB.trains[ydtrainNam]["consistNum"]
            consistNam = "consist"+str(consistNum)
            if mVars.prms["dbgYdProc"]: print("brkDownTrain: ", ydtrainNam, "consist: ", trainDB.consists[consistNam])
            self.thisConsist = trainDB.consists[consistNam]["stops"][loc]
            if mVars.prms["dbgYdProc"]: print("consist core: ", self.thisConsist)
            
            carSel, typeCount = carProcObj.carTypeSel(self.thisConsist)
            if dbgLocal: print("brkDnTrn: carSel: ", carSel)
            #if typeCount <= 0: return

            idx = 0
            while ((idx < rate) and (typeCount > 0)):
                carClassType = carProcObj.randomCar(carSel)
                idx +=1
            # remove cars from consist and assign to destination trackTots
                if self.thisConsist[carClassType] >0:
                    self.thisConsist[carClassType] = self.thisConsist[carClassType] - 1
                    destTrack = self.randomTrack()
                    locs.locDat[loc]["trackTots"][destTrack] +=1
                    locs.locDat[loc]["tracks"][destTrack][carClassType] +=1
                    typeCount -=1
            
            if dbgLocal: print("brkDownTrain: after while loop: typeCount = ", typeCount, ", ydTrainNam = ", ydtrainNam)
            #if ydtrainNam in self.ydTrains["brkDnTrn"]: print("found ydtrainNam")
            if typeCount == 0:
                #remove train name from ydTrains and locs.locData
                self.rmTrnFromLoc("brkDnTrn", loc, ydtrainNam)
                trainDB.trains.pop(ydtrainNam)

        try:
            trainDB.consists[consistNum]["stops"][loc] = self.thisConsist
        except:
            pass

    def rmTrnFromLoc(self, action, loc, ydtrainNam):
        index = self.ydTrains[action].index(ydtrainNam)
        self.ydTrains[action].pop(index)
        if dbgLocal: print("after removal: ydTrains: ", self.ydTrains)
        
        index = locs.locDat[loc]["trains"].index(ydtrainNam)
        locs.locDat[loc]["trains"].pop(index)
        
    def buildTrain(self, loc):
        numCarsAvail = 0
        #if mVars.prms["dbgYdProc"]: print("buildTrain: number of cars available: ", numCarsAvail)
        
        # yard has no train undergoing build
        if not self.ydTrains["buildTrain"]:
            
            self.buildNewTrain(loc)
            
            
        # yard has a train already building; add cars to it
        # single train is allowed to build in a yard
        else:         
            self.add2Train(loc)  
            ydtrainNam =  ''.join(self.ydTrains["buildTrain"])
            trainStem = trainDB.trains[ydtrainNam]

            if trainStem["numCars"] >= mVars.prms["trainSize"]*0.7:
                # train has reached max size
                trainStem["status"] = "ready2Leave"
                route4newTrn = self.findRoutes(loc, ydtrainNam)
                dest = trainDB.trains[ydtrainNam]["nextLoc"]

                leftObj = mVars.routes[route4newTrn]["leftObj"]
                rtObj = mVars.routes[route4newTrn]["rtObj"]
                mVars.routes[route4newTrn]["trains"].append(ydtrainNam)
                if loc == leftObj.strip(): 
                    trainStem["direction"] = "east"
                    trainStem["xTrnInit"] = gui.guiDict[loc]["x1"]
                elif loc == rtObj.strip():
                    trainStem["direction"] = "west"
                    trainStem["xTrnInit"] = gui.guiDict[loc]["x0"] - trainParams.trnLength
                else: print("built train", ydtrainNam,  "leftObj: ", leftObj, "rtObj: "
                            , rtObj,"loc: ", loc, "direction: ", trainStem["direction"])

                trainStem["currentLoc"] = route4newTrn
                if mVars.prms["dbgYdProc"]: print("train",ydtrainNam," built: "
                                ,trainStem,
                                ", route: ", mVars.routes[route4newTrn])
                self.rmTrnFromLoc("buildTrain", loc, ydtrainNam)


    def findRoutes(self, loc, ydtrainNam):
        for routeNam in mVars.routes:
            loc = ''.join(loc)
            dest = ''.join(trainDB.trains[ydtrainNam]["nextLoc"])
            if dbgLocal: print("routNam: ", routeNam, " loc: ", loc, 
                " nextLoc: ", dest, "route: ", mVars.routes[routeNam])
            if (loc in mVars.routes[routeNam].values()) and \
                (dest in mVars.routes[routeNam].values()):
                return routeNam

                            
    def buildNewTrain(self, loc):
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
                self.ydTrains["buildTrain"].append(trnName)
                locs.locDat[loc]["trains"].append(trnName)
                return

    
    def add2Train(self, loc):
        from carProc import carProc
        carProcObj = carProc()
        rate = mVars.geometry[loc]["classRate"]
        ydtrainNam =  ''.join(self.ydTrains["buildTrain"])
        locStem = locs.locDat[loc]
        trainStem = trainDB.trains[ydtrainNam]
        
        trainDest = trainStem["nextLoc"]
        consistNum = trainStem["consistNum"]
        consistNam = "consist"+str(consistNum)
        numCars = trainStem["numCars"]
        print("building train: ", ydtrainNam, "numCars: ", numCars , ", consist: ", trainDB.consists[consistNam], ", destination: ", trainDest)
        self.bldConsist = trainDB.consists[consistNam]["stops"][trainDest]
        thisTrack = locStem["tracks"][trainDest]
        
        if mVars.prms["dbgYdProc"]: print("buildTrain: before next build step, consist : ", 
                self.bldConsist,
                "\ntrack contents: ", thisTrack)
        
        if locStem["trackTots"][trainDest] == 0: return
        carSel, typeCount = carProcObj.carTypeSel(thisTrack)
        carClassType = carProcObj.randomCar(carSel)
        carsClassed = 0
        while ((carsClassed < rate) and (typeCount > 0)):

            carsClassed +=1
            if thisTrack[carClassType] >0:
                thisTrack[carClassType] -=1
                locStem["trackTots"][trainDest] -=1
                self.bldConsist[carClassType] +=1
                trainStem["numCars"] +=1
                typeCount -=1

        try:
            trainDB.consists[consistNum]["stops"][loc] = self.bldConsist
            locStem["tracks"][trainDest] = thisTrack
        except:
            pass
        if mVars.prms["dbgYdProc"]: print("buildTrain: after build step, consist : ", 
                self.bldConsist,
                "\ntrack contents: ", thisTrack)
            
    def classCars(self):
        pass
    def servIndus(self):
        pass
    # calc trains that arrive, trains ready to leave (and do they?)
    # cars classified; need a dict with all car types, next dest (track or 
    # loc), status (ready to classify, classified, in arriving train)
        #self.trainOut = self.rateClassification*self.fracTrainBuild/mVars.trainSize


