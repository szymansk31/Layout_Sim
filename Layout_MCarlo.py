import numpy as np
import json
import tkinter as tk
from tkinter import ttk
 
            
#=================================================
class locProc():
    
    def __init__(self):
        self.thisLoc = {}
        pass
    def analyzeTrains(self):
        for trainIDX in self.thisloc["trains"]:
            match mVars.trains[trainIDX]:
                case "enterYard":
                    pass
        
    def breakDownTrain(self):
        pass
    def buildTrain(self):
        pass
    def classifyCars(self):
        pass
    def servIndus(self):
        pass
    def yardCalcs(self, thisloc, loc):
        self.thisLoc = thisloc
            
    # calc trains that arrive, trains ready to leave (and do they?)
    # cars classified; need a dict with all car types, next dest (track or 
    # loc), status (ready to classify, classified, in arriving train)
        #self.trainOut = self.rateClassification*self.fracTrainBuild/mVars.trainSize


#=================================================
class trainProc():
    numTrains = 0
    def __init__(self):
        #self.trainID = int
        pass
        
    def initTrain():
        print("\n creating train dictionary ", trainProc.numTrains)
        try: 
            jsonFile = open (files.trainDictFile, "r")
            trainDict = json.load(jsonFile)
            jsonFile.close()
            trainProc.numTrains +=1
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        print("trainDict: ", trainDict)
        return trainDict

        
    def trainCalcs(self, trainDict):
        match trainDict["status"]:
            case "enroute":
                variance = np.random.normal(loc=0, scale=0.25, size=1)
                timeEnRoute = trainDict["timeEnRoute"] + vars.prms["timeStep"] + variance
                trainDict["timeEnRoute"] = timeEnRoute
                route = trainDict["currentLoc"]
                transTime = vars.routes[trainDict["currentLoc"]]["transTime"]
                print("trainCalcs: train: ", trainDict["trainNum"], "route: ", route, 
                    ", transTime:", transTime, ", timeEnRoute: ", timeEnRoute,
                    ", variance: ", variance)
                if trainDict["timeEnRoute"] >= transTime:
                    trainDict["currentLoc"] = vars.routes[trainDict["currentLoc"]]["dest"]
                    geometry[trainDict["currentLoc"]]["trains"].append(trainDict["trainNum"])
                    trainDict["status"] = "enterYard"
                    trainDict["timeEnRoute"] = 0
                    vars.numOpBusy -=1
                    
            case "enterYard":
                pass
            case "leaving":
                pass
            case "switching":
                pass
            
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
vars = mVars()
vars.readParams(files)

from layoutGeom import layoutGeom
layout = layoutGeom()
geometry = mVars.geometry = layout.readLayoutGeom(files)
vars.routes = layout.defRoutes(geometry)

trainObj = trainProc()
train1 = trainProc.initTrain()

vars.trains.append(train1)
print("trains: ", vars.trains)

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
print("vars.time: ", vars.time, "maxtime: ", vars.prms["maxTime"])
while vars.time < vars.prms["maxTime"]:
    for trainIDX in range(len(vars.trains)):
        trainObj.trainCalcs(vars.trains[trainIDX])
    count +=1
    if count == maxCount:
        print("trainDict[",trainIDX,"] = ", vars.trains[trainIDX])
        currentLoc = vars.trains[trainIDX]["currentLoc"]
        if "route" not in currentLoc:
            print("\nloc[",currentLoc,"]", geometry[currentLoc])
        count = 0
    for loc in geometry:
        ydProc.yardCalcs(geometry, loc)
    vars.time +=1
# 
# Create root object 
# and window
"""
vars.trains.append(train1)
vars.trains.remove(train1)
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
