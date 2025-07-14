import random
import numpy as np
from mainVars import mVars
from locProc import locs
from stateVars import locs, trainDB, routeCls
from gui import gui
np.set_printoptions(precision=2, suppress=True) 

dbgLocal = 1          
class swArea():
    
    def __init__(self):
        self.thisConsist = {}
        from locProc import locProc
        self.locProcObj = locProc()
        pass
  
    def switchArea(self, thisLoc, loc, ydTrainsIn):
        self.ydTrains = ydTrainsIn
        
        for action in ydTrainsIn:
            match action:
                case "continue":
                    self.locProcObj.startTrain(action, loc, ydtrainNam)
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
                    while waitIdx < mVars.prms["miscWaitTime"]:
                        waitIdx +=1
                        pass

        from carProc import carProc
        carProcObj = carProc()
        rate = mVars.geometry[loc]["classRate"]
        for ydtrainNam in self.ydTrains["roadCrewSw"]:
            consistNum = trainDB.trains[ydtrainNam]["consistNum"]
            consistNam = "consist"+str(consistNum)
            if mVars.prms["dbgYdProc"]: print("swArea: ", ydtrainNam, "consist: ", trainDB.consists[consistNam])
            self.thisConsist = trainDB.consists[consistNam]["stops"][loc]
            if mVars.prms["dbgYdProc"]: print("consist core: ", self.thisConsist)
            
            carSel, availCars = carProcObj.carTypeSel(self.thisConsist)
            if dbgLocal: print("swArea: carSel: ", carSel)
            #if availCars <= 0: return

            idx = 0
            while ((idx < rate) and (availCars > 0)):
                carClassType = carProcObj.randomCar(carSel)
                idx +=1
            # remove cars from consist and assign to destination trackTots
                if self.thisConsist[carClassType] >0:
                    self.thisConsist[carClassType] = self.thisConsist[carClassType] - 1
                    destTrack = self.randomTrack()
                    locs.locDat[loc]["trackTots"][destTrack] +=1
                    locs.locDat[loc]["tracks"][destTrack][carClassType] +=1
                    availCars -=1
            
            if dbgLocal: print("brkDownTrain: after while loop: availCars = ", availCars, ", ydTrainNam = ", ydtrainNam)
            #if ydtrainNam in self.ydTrains["brkDnTrn"]: print("found ydtrainNam")
            if availCars == 0:
                #remove train name from ydTrains and locs.locData
                self.rmTrnFromLoc("brkDnTrn", loc, ydtrainNam)
                trainDB.trains.pop(ydtrainNam)

        try:
            trainDB.consists[consistNum]["stops"][loc] = self.thisConsist
        except:
            pass

    def buildTrain(self, loc):
        from trainProc import trainParams
        trainObj = trainParams()

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

                leftObj = routeCls.routes[route4newTrn]["leftObj"]
                rtObj = routeCls.routes[route4newTrn]["rtObj"]
                routeCls.routes[route4newTrn]["trains"].append(ydtrainNam)
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
                                ", route: ", routeCls.routes[route4newTrn])
                self.rmTrnFromLoc("buildTrain", loc, ydtrainNam)


                            
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
        carSel, availCars = carProcObj.carTypeSel(thisTrack)
        carClassType = carProcObj.randomCar(carSel)
        carsClassed = 0
        while ((carsClassed < rate) and (availCars > 0)):

            carsClassed +=1
            if thisTrack[carClassType] >0:
                thisTrack[carClassType] -=1
                locStem["trackTots"][trainDest] -=1
                self.bldConsist[carClassType] +=1
                trainStem["numCars"] +=1
                availCars -=1

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


