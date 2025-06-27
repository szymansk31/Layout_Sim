import numpy as np
import json
import tkinter as tk
from tkinter import ttk
import random
 
            
#=================================================
class locProc():
    
    def __init__(self):
        self.thisLoc = {}
        self.actionList = ["brkDownTrain", "swTrain", "buildTrain", "classCars", "servIndus", "misc"]
        self.weights = [0.3, 0.3, 0.3, 0.1]
        self.ydTrains = {"brkDownTrain": [], "swTrain": [], "buildTrain": []}
        mVars.locs = {}

    def yardCalcs(self, thisloc, loc):
        self.thisLoc = thisloc
        self.analyzeTrains(thisloc, loc)
        match random.choices(self.actionList, weights=self.weights, k=1):
            case "brkDownTrain":
                self.brkDownTrain(loc)
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
            match mVars.trains[trainIDX]["status"]:
                case "terminate":
                    self.ydTrains["brkDownTrain"].append(trainIDX)
                case "swTrain":
                    self.ydTrains["swTrain"].append(trainIDX)
        
    def brkDownTrain(self, loc):
        from carProc import randomCar, carTypeSel
        carProcObj = carProc()
        rate = mVars.geometry[loc]["classRate"]
        for ydtrainNum in self.ydTrains["brkDownTrain"]:
            consistNum = mVars.trains[ydtrainNum]["consistNum"]
            consist = mVars.consists[consistNum]
            carSel, typeCount = carProcObj.carTypeSel(consist, loc)
            if mVars.prms.debugYardProc: print("brkDownTrain: carSel: ", carSel)
            if typeCount < rate: typeCount = rate
            while typeIdx < typeCount:
                carClassType = carProcObj.randomCar(carSel)
                typeIdx +=1
            # remove cars from consist
                consist["stops"][loc][carClassType] = consist["stops"][loc][carClassType] - 1
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


            
#=================================================
class swAreaProc():
    yardName = str
    numTracks  = int
    numDest = int
    fracTrainBuild = int        #fraction of classified cars built into trains
    rateClassification = int    #num cars classified/time
    numAdjYards = int           #num adjacent yards
    adjYardNames = []
    time2AdjYards = []
    trainOut = int
    swAreaNames = []
    
    
    def __init__(self):
        pass
    
    def swAreaSetup(self):
        print("\nsetting up switching area ", self.swAreaNames)
        
        
    def swAreaCalcs(self):
        self.trainOut = self.rateClassification*self.fracTrainBuild/mVars.trainSize
    
            

#########################################################
# start of code
#########################################################

#def main():    
# Open Excel file
from fileNamesIO import fileNames
files = fileNames()
#from sharedVars import frmsWind, indices, carHdr
#idxObj = indices()
#frames = frmsWind()

# Open sheets and populate data lists
#getCarInfo(excelFile)
# read paramDict from last save (overwrites excel file 
# contents with changes from Car_Cards)

from mainVars import mVars
mVars.readParams(files)

from layoutGeom import layoutGeom
layout = layoutGeom()
geometry = mVars.geometry = layout.readLayoutGeom(files)  #geometry is for input to local processing
mVars.routes = layout.defRoutes(geometry)

from trainCalcs import trainProc
trainObj = trainProc()
train1 = trainObj.initTrain(files)

mVars.trains.append(train1)
if mVars.prms.debugTrainDict: print("trains: ", mVars.trains)

#setup initial car distribution
from carProc import carProc
carProcObj = carProc()
carDict = carProcObj.readCarInitInfo(files)
carProcObj.procCarFileInfo(carDict)

ydProc = locProc()
idx = 0
count = 0
maxCount = 7
print("\n")
for loc in geometry:
    if mVars.prms.debugGeom: print("location: ", loc, ", index: ", idx, ": ", geometry[loc])
    idx +=1

#main loop:
print("mVars.time: ", mVars.time, "maxtime: ", mVars.prms["maxTime"])
while mVars.time < mVars.prms["maxTime"]:
    for trainIDX in range(len(mVars.trains)):
        trainObj.trainCalcs(mVars.trains[trainIDX])
    count +=1
    if count == maxCount:
        if mVars.prms.debugTrainProc: print("trainDict[",trainIDX,"] = ", mVars.trains[trainIDX])
        currentLoc = mVars.trains[trainIDX]["currentLoc"]
        if "route" not in currentLoc:
            print("\nloc[",currentLoc,"]", geometry[currentLoc])
        count = 0
    for loc in geometry:
        ydProc.yardCalcs(geometry, loc)
    mVars.time +=1
