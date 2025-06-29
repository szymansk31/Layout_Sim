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
        self.actionList = ["brkDnTrn", "swTrain", "buildTrain", "classCars", "servIndus", "misc"]
        #self.weights = [0.18, 0.18, 0.18, 0.18, 0.18, 0.1]
        self.weights = [1, 0, 0, 0, 0, 0]
        self.ydTrains = {"brkDnTrn": [], "swTrain": [], "buildTrain": []}
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
        for dest in locs.locDat[loc]["tracks"]:
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
                    if dbgLocal: print("this location tracks: ", locs.locDat[loc]["tracks"])
                pass
            case "swTrain":
                pass
            case "buildTrain":
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
        
    def brkDownTrain(self, loc):
        from carProc import carProc
        carProcObj = carProc()
        rate = mVars.geometry[loc]["classRate"]
        for ydtrainNam in self.ydTrains["brkDnTrn"]:
            consistNum = trainDB.trains[ydtrainNam]["consistNum"]
            consistNam = "consist"+str(consistNum)
            self.thisConsist = trainDB.consists[consistNam]["stops"][loc]
            
            carSel, typeCount = carProcObj.carTypeSel(self.thisConsist, loc)
            if dbgLocal: print("brkDnTrn: carSel: ", carSel)
            #if typeCount <= 0: return

            idx = 0
            while ((idx < rate) and (typeCount > 0)):
                carClassType = carProcObj.randomCar(carSel)
                carClassType = ''.join(carClassType)
                idx +=1
            # remove cars from consist and assign to destination tracks
                if self.thisConsist[carClassType] >0:
                    self.thisConsist[carClassType] = self.thisConsist[carClassType] - 1
                    destTrack = self.randomTrack()
                    locs.locDat[loc]["tracks"][destTrack] +=1
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

        
    def buildTrain(self):
        pass
    def classCars(self):
        pass
    def servIndus(self):
        pass
    # calc trains that arrive, trains ready to leave (and do they?)
    # cars classified; need a dict with all car types, next dest (track or 
    # loc), status (ready to classify, classified, in arriving train)
        #self.trainOut = self.rateClassification*self.fracTrainBuild/mVars.trainSize


