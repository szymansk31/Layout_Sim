import numpy as np
import json
import random
from mainVars import mVars
from trainProc import trainDB
 
            
#=================================================
class locProc():
    
    def __init__(self):
        self.thisLoc = {}
        self.actionList = ["brkDownTrain", "swTrain", "buildTrain", "classCars", "servIndus", "misc"]
        #self.weights = [0.18, 0.18, 0.18, 0.18, 0.18, 0.1]
        self.weights = [1, 0, 0, 0, 0, 0]
        self.ydTrains = {"brkDownTrain": [], "swTrain": [], "buildTrain": []}
        mVars.locs = {}

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
        for trainIDX in thisLoc[loc]["trains"]:
            match trainDB.trains[trainIDX]["status"]:
                case "terminate":
                    if trainIDX not in self.ydTrains["brkDownTrain"]:
                        self.ydTrains["brkDownTrain"].append(trainIDX)
                case "dropPickup":
                    if trainIDX not in self.ydTrains["swTrain"]:
                        self.ydTrains["swTrain"].append(trainIDX)
        
    def brkDownTrain(self, loc):
        from carProc import carProc
        carProcObj = carProc()
        rate = mVars.geometry[loc]["classRate"]
        for ydtrainNum in self.ydTrains["brkDownTrain"]:
            consistNum = trainDB.trains[ydtrainNum]["consistNum"]
            consist = trainDB.consists[consistNum]
            carSel, typeCount = carProcObj.carTypeSel(consist, loc)
            if mVars.prms["debugYardProc"]: print("brkDownTrain: carSel: ", carSel)
            if typeCount < rate: typeCount = rate
            while typeIdx < typeCount:
                carClassType = carProcObj.randomCar(carSel)
                typeIdx +=1
            # remove cars from consist
                consist["stops"][loc][carClassType] = consist["stops"][loc][carClassType] - 1
        try:
            trainDB().consists[consistNum] = consist
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


