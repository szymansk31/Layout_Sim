import numpy as np
import json
import tkinter as tk
from tkinter import ttk
from mainVars import *
 
            
#=================================================
class yardProc():
    
    def __init__(self):
        yardName = str
        numTracks  = int
        numDest = int
        fracTrainBuild = int        #fraction of classified cars built into trains
        rateClassification = int    #num cars classified/time
        numAdjYards = int           #num adjacent yards
        adjYardNames = []
        time2AdjYards = []
        trainOut = int

    
    def yardSetup(self):
        print("\nsetting up yard ", self.yardName)
        
        
    def yardCalcs(self):
        self.trainOut = self.rateClassification*self.fracTrainBuild/mainVar.trainSize
    
#=================================================
class trainProc():
    numTrains = 0
    def __init__(self):
        #self.trainID = int
        pass
        
    def initTrainDict():
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

        
    def trainCalcs(self):
        self.trainOut = self.rateClassification*self.fracTrainBuild/mainVar.trainSize
    
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
        self.trainOut = self.rateClassification*self.fracTrainBuild/mainVar.trainSize
    
            

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

vars = mainVar()
vars.readParams()

train1 = trainProc.initTrainDict()

vars.trains.append(train1)
print("trains: ", vars.trains)
# 
# Create root object 
# and window

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

#if __name__=="__main__":
#    main()
