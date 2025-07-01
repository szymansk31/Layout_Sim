import numpy as np
import json
import random
from mainVars import mVars
from trainProc import trainDB
from layoutGeom import geom
 
dbgLocal = 1      
#=================================================
class locs():
    locDat = {}
#=================================================
class locProc():
    
    def __init__(self):
        self.thisLoc = {}
        self.thisConsist = {}
        self.actionList = ["brkDnTrn", "swTrain", "bldTrn", "classCars", "servIndus", "misc"]
        #self.weights = [0.18, 0.18, 0.18, 0.18, 0.18, 0.1]
        self.weights = [0.5, 0, 0.5, 0, 0, 0]
        self.ydTrains = {"brkDnTrn": [], "swTrain": [], "bldTrn": []}
        self.thisLocDests = []
        from fileProc import readFiles
        files = readFiles()
        print("initializing location dicts: ")
        locs.locDat = files.readFile("locationFile")
    #classmethod:
    
    def randomTrack(self):
        return ''.join(random.choice(self.thisLocDests))

    def yardCalcs(self, thisloc, loc):
        self.thisLoc = thisloc
        self.thisLocDests = []
        if mVars.prms["dbgYdProc"]: print("entering yardCalcs: locdat: "
                    , locs.locDat[loc])
        for dest in locs.locDat[loc]["trackTots"]:
            self.thisLocDests.append(dest)
        #if mVars.prms["\ndbgYdProc"]: print("yardCalcs: thisLoc ", thisloc)
        self.analyzeTrains(loc)
        if mVars.prms["dbgYdProc"]: print("trains analyzed: ydTrains: ", self.ydTrains)

        choice = random.choices(self.actionList, weights=self.weights, k=1)
        choice = ''.join(choice)
        if mVars.prms["dbgYdProc"]: print("\nchoice: ", choice)
        match choice:
            case "brkDnTrn":
                self.brkDownTrain(loc)
                if mVars.prms["dbgYdProc"]: 
                    if dbgLocal: print("after brkDnTrn: consist: ", 
                    self.thisConsist)
                    if dbgLocal: print("this location trackTots: ", locs.locDat[loc]["trackTots"])
                pass
            case "swTrain":
                pass
            case "bldTrn":
                self.buildTrain(loc)
                pass
            case "classCars":
                pass
            case "servIndus":
                pass
            case "misc":
                pass
            
    def analyzeTrains(self, loc):
        self.ydTrains = {"brkDnTrn": [], "swTrain": [], "buildTrain": []}

        for trainNam in locs.locDat[loc]["trains"]:
            match trainDB.trains[trainNam]["status"]:
                case "terminate":
                    if trainNam not in self.ydTrains["brkDnTrn"]:
                        self.ydTrains["brkDnTrn"].append(trainNam)
                case "dropPickup":
                    if trainNam not in self.ydTrains["swTrain"]:
                        self.ydTrains["swTrain"].append(trainNam)
                case "building":
                    if trainNam not in self.ydTrains["swTrain"]:
                        self.ydTrains["buildTrain"].append(trainNam)

        
    def brkDownTrain(self, loc):
        from carProc import carProc
        carProcObj = carProc()
        rate = mVars.geometry[loc]["classRate"]
        for ydtrainNam in self.ydTrains["brkDnTrn"]:
            consistNum = trainDB.trains[ydtrainNam]["consistNum"]
            consistNam = "consist"+str(consistNum)
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
                    locs.locDat[loc]["cars"][destTrack][carClassType] +=1
                    typeCount -=1
            
            if dbgLocal: print("brkDownTrain: after while loop: typeCount = ", typeCount, ", ydTrainNam = ", ydtrainNam)
            #if ydtrainNam in self.ydTrains["brkDnTrn"]: print("found ydtrainNam")
            if typeCount == 0:
                #remove train name from ydTrains and locs.locData
                index = self.ydTrains["brkDnTrn"].index(ydtrainNam)
                self.ydTrains["brkDnTrn"].pop(index)
                if dbgLocal: print("after removal: ydTrains: ", self.ydTrains)
                
                index = locs.locDat[loc]["trains"].index(ydtrainNam)
                locs.locDat[loc]["trains"].pop(index)

        try:
            trainDB.consists[consistNum]["stops"][loc] = self.thisConsist
        except:
            pass

        
    def buildTrain(self, loc):
        numCarsAvail = 0

        for trackTots in locs.locDat[loc]["trackTots"]:
            if "indust" not in trackTots:
                numCarsAvail += locs.locDat[loc]["trackTots"][trackTots]
        
        if mVars.prms["dbgYdProc"]: print("bldTrn: number of cars available: ", numCarsAvail)
        # yard has no train undergoing build
        if not self.ydTrains["buildTrain"]:
            self.buildNewTrain(loc)
            
            
        # yard has train building; add cars to it
        # single train is max number building in a yard
        else:         
            self.add2Train(loc)  
            ydtrainNam =  self.ydTrains["buildTrain"]

            if trainDB.trains[ydtrainNam]["numCars"] >= mVars.prms["trainSize"]:
                # train has reached max size
                trainDB.trains[ydtrainNam]["status"] = "ready2Leave"
            if mVars.prms["dbgYdProc"]: print("train",ydtrainNam," built: ",trainDB.trains[ydtrainNam])

                            
    def buildNewTrain(self, loc):
        from carProc import carProc
        genExp = (trackTot for trackTot in locs.locDat[loc]["trackTots"] if "indust" not in trackTot)
        for trackTots in genExp:
            if locs.locDat[loc]["trackTots"][trackTots] >= mVars.prms["trainSize"]*0.5:
                trainObj = trainDB()
                trainNum, consistNum = trainObj.newTrain()
                newTrainNam = "train"+str(trainNum)

                trainDB.trains[newTrainNam].update( {
                    "status": "building",
                    "origLoc": loc,
                    "finalLoc": "",
                    "currentLoc": loc,
                    "numStops": 1,
                    "stops": [trackTots]                   
                        })
                print("new train: ", newTrainNam, ": ", trainDB.trains)
                self.ydTrains["buildTrain"].append(newTrainNam)
                locs.locDat[loc]["trains"].append(newTrainNam)

        
    def add2Train(self, loc):
        from carProc import carProc
        carProcObj = carProc()
        rate = mVars.geometry[loc]["classRate"]

        ydtrainNam =  ''.join(self.ydTrains["buildTrain"])
        trainDest = trainDB.trains[ydtrainNam]["finalLoc"]
        
        consistNum = trainDB.trains[ydtrainNam]["consistNum"]
        consistNam = "consist"+str(consistNum)
        self.thisConsist = trainDB.consists[consistNam]["stops"][trainDest]
        thisTrack = locs.locDat[loc]["cars"][trainDest]
        
        if mVars.prms["dbgYdProc"]: print("bldTrn: before next build step, consist : ", 
                self.thisConsist,
                "\ntrack contents: ", thisTrack)
        
        carSel, typeCount = carProcObj.carTypeSel(thisTrack)
        carClassType = carProcObj.randomCar(carSel)
        carsClassed = 0
        while ((carsClassed < rate) and (typeCount > 0)):
            #trainDB.trains[]
            carsClassed +=1
            if thisTrack[carClassType] >0:
                thisTrack[carClassType] -=1
                locs.locDat[loc]["trackTots"][trainDest] -=1
                self.thisConsist[carClassType] +=1
                typeCount -=1

        try:
            trainDB.consists[consistNum]["stops"][loc] = self.thisConsist
            locs.locDat[loc]["cars"][trainDest] = thisTrack
        except:
            pass
        if mVars.prms["dbgYdProc"]: print("bldTrn: after build step, consist : ", 
                self.thisConsist,
                "\ntrack contents: ", thisTrack)
            


    def classCars(self):
        pass
    def servIndus(self):
        pass
    # calc trains that arrive, trains ready to leave (and do they?)
    # cars classified; need a dict with all car types, next dest (track or 
    # loc), status (ready to classify, classified, in arriving train)
        #self.trainOut = self.rateClassification*self.fracTrainBuild/mVars.trainSize


