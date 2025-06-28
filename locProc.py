import numpy as np
import json
import random
from mainVars import mVars
from trainProc import trainDB
from layoutGeom import geom
 
         
#=================================================
class locs():
    locs = {}
#=================================================
class locProc():
    
    def __init__(self):
        self.thisLoc = {}
        self.wrkngConsist = {}
        self.actionList = ["brkDownTrain", "swTrain", "buildTrain", "classCars", "servIndus", "misc"]
        #self.weights = [0.18, 0.18, 0.18, 0.18, 0.18, 0.1]
        self.weights = [1, 0, 0, 0, 0, 0]
        self.ydTrains = {"brkDownTrain": [], "swTrain": [], "buildTrain": []}
        from fileProc import readFiles
        files = readFiles()
        print("initializing location dicts: ")
        locs.locs = files.readFile("locationFile")
    #classmethod:

    def yardCalcs(self, thisloc, loc):
        self.thisLoc = thisloc
        #if mVars.prms["\ndebugYardProc"]: print("yardCalcs: thisLoc ", thisloc)
        self.analyzeTrains(thisloc, loc)
        if mVars.prms["debugYardProc"]: print("trains analyzed: ydTrains: ", self.ydTrains)
        #match random.choices(self.actionList, weights=self.weights, k=1):
        choice = random.choices(self.actionList, weights=self.weights, k=1)
        choice = ''.join(choice)
        if mVars.prms["debugYardProc"]: print("choice: ", choice)
        match choice:
            case "brkDownTrain":
                self.brkDownTrain(loc)
                if mVars.prms["debugYardProc"]: print("\nafter brkDownTrain: consist: ", 
                    trainDB.consists)
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
            
    def analyzeTrains(self, thisLoc, loc):
        self.ydTrains = {"brkDownTrain": [], "swTrain": [], "buildTrain": []}

        for trainNam in thisLoc[loc]["trains"]:
            match trainDB.trains[trainNam]["status"]:
                case "terminate":
                    if trainNam not in self.ydTrains["brkDownTrain"]:
                        self.ydTrains["brkDownTrain"].append(trainNam)
                case "dropPickup":
                    if trainNam not in self.ydTrains["swTrain"]:
                        self.ydTrains["swTrain"].append(trainNam)
        
    def brkDownTrain(self, loc):
        from carProc import carProc
        carProcObj = carProc()
        rate = mVars.geometry[loc]["classRate"]
        for ydtrainNum in self.ydTrains["brkDownTrain"]:
            consistNum = trainDB.trains[ydtrainNum]["consistNum"]
            consistNam = "consist"+str(consistNum)
            consist = trainDB.consists[consistNam]["stops"][loc]
            
            carSel, typeCount = carProcObj.carTypeSel(consist, loc)
            if mVars.prms["debugYardProc"]: print("brkDownTrain: carSel: ", carSel)
            if typeCount <= 0: return
            if typeCount < rate: typeCount = rate
            typeIdx = 0
            while typeIdx < rate:
                carClassType = carProcObj.randomCar(carSel)
                carClassType = ''.join(carClassType)
                typeIdx +=1
            # remove cars from consist
                if consist[carClassType] >0:
                    consist[carClassType] = consist[carClassType] - 1
        try:
            trainDB().consists[consistNum]["stops"][loc] = consist
        except:
            pass
# assign cars to destinations randomly

        
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


