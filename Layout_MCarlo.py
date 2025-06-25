import numpy as np
import json
import tkinter as tk
from tkinter import ttk
import random
 
            
#=================================================
class locProc():
    
    def __init__(self):
        self.thisLoc = {}
        self.actionList = ["classifyTrain", "buildTrain", "classifyCars", "servIndus"]
        self.weights = [0.3, 0.3, 0.3, 0.1]
        mVars.locs = {}

    def initLocationInfo(files):
        print("\n creating location dictionary ")
        try: 
            jsonFile = open (files.locInfoFile, "r")
            locDict = json.load(jsonFile)
            jsonFile.close()
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        print("locDict: ", locDict)
        return locDict

    def yardCalcs(self, thisloc, loc):
        self.thisLoc = thisloc
        self.analyzeTrains(thisloc, loc)
        match random.choices(self.actionList, weights=self.weights, k=1):
            case "classifyTrain":
                self.classifyTrain()
                pass
            case "buildTrain":
                pass
            case "classifyCars":
                pass
            case "servIndus":
                pass
            
    def analyzeTrains(self, thisLoc, loc):
        for trainIDX in thisLoc[loc]["trains"]:
            match mVars.trains[trainIDX]["status"]:
                case "enterYard":
                    self.classifyTrain()
                    pass
        
    def classifyTrain(self):
        pass
    def buildTrain(self):
        pass
    def classifyCars(self):
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
train1 = trainProc.initTrain(files)

mVars.trains.append(train1)
print("trains: ", mVars.trains)

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
    print("location: ", loc, ", index: ", idx, ": ", geometry[loc])
    idx +=1

#main loop:
print("mVars.time: ", mVars.time, "maxtime: ", mVars.prms["maxTime"])
while mVars.time < mVars.prms["maxTime"]:
    for trainIDX in range(len(mVars.trains)):
        trainObj.trainCalcs(mVars.trains[trainIDX])
    count +=1
    if count == maxCount:
        print("trainDict[",trainIDX,"] = ", mVars.trains[trainIDX])
        currentLoc = mVars.trains[trainIDX]["currentLoc"]
        if "route" not in currentLoc:
            print("\nloc[",currentLoc,"]", geometry[currentLoc])
        count = 0
    for loc in geometry:
        ydProc.yardCalcs(geometry, loc)
    mVars.time +=1
# 
# Create root object 
# and window
"""
mVars.trains.append(train1)
mVars.trains.remove(train1)
"""

"""
editWindow = tk.Tk() 
#editWindow = tk.Toplevel(root)
editWindow.title("Car Card Selection")
# Adjust size 
editWindow.geometry( "800x600" ) 


frames.setFrms(editWindow, tk)

global tabControl
tabControl = ttk.Notebook(editWindow)
createTabs(tabControl)
"""
"""
tabControl.grid(row=tabRow, column=tabCol, sticky="nw")
for idx in range(numTabs):
    createRRLists(sheetNames[idx], tabs[idx], rrBox)
    tabContents(sheetNames[idx], tabs[idx], frames)
    
setXLOutFname(fileNameEntry)

# Execute tkinter 
editWindow.mainloop()
"""
