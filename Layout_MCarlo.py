import xlrd
import xlsxwriter
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
class roadTrainProc():
    
    def __init__(self):
        self.trainID = int
    
    def readTrainDict(self):
        print("\nreading train dictionary ", self.trainID)
        try: 
            jsonFile = open ("trainDict.txt", "r")
            trainDict = json.load(jsonFile)
            jsonFile.close()
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        print("trainDict: ", trainDict)
        
    def roadTrainCalcs(self):
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
    
    
    def __init__(self):
        pass
    
    def swAreaSetup(self):
        print("\nsetting up switching area ", self.swAreaName)
        
        
    def swAreaCalcs(self):
        self.trainOut = self.rateClassification*self.fracTrainBuild/mainVar.trainSize
    
    
#=================================================
class fileIO():
    def __init__(self):
        self.procObj  
    
    def writeCardPage(tmpFileName):
        print("\nwriting card page")
        print("writing paramDictFile: ", tmpFileName, " and closing xlsx file: ", files.xlsxOutputFile)
        with open (tmpFileName, "w") as jsonFile:
            json.dump(paramDict, jsonFile)
        try:    
            xlsxWorkbook.close()
        except:
            print("\nworkbook does not exist; starting new")


#=================================================
        

#########################################################
# start of code
#########################################################

#def main():    
# Open Excel file
from fileNameSetup import fileNames
files = fileNames()
#from sharedVars import frmsWind, indices, carHdr
#idxObj = indices()
#frames = frmsWind()

#excelFile = xlrd.open_workbook(files.excelDBFile)
#print("opened excel file: ", files.excelDBFile)

# Open sheets and populate data lists
#getCarInfo(excelFile)
# read paramDict from last save (overwrites excel file 
# contents with changes from Car_Cards)

paramObj = mainVar()
paramObj.readParams()

trainObj = roadTrainProc()
trainObj.readTrainDict()

#paramObj.createOptionlists()
#if (debug):
#    print("optionLists = ", optionLists)

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
