import xlrd
import xlsxwriter
import numpy as np
import json
import tkinter as tk
from tkinter import ttk
from mainVars import *
 
            
#=================================================
class yardProc():
    yardName = str
    numTracks  = int
    numDest = int
    fracTrainBuild = int        #fractino of classified cars built into trains
    rateClassification = int    #num cars classified/time
    numAdjYards = int           #num adjacent yards
    adjYardNames = []
    time2AdjYards = []
    trainOut = int
    
    
    def __init__(self):
        pass
    
    def yardSetup(self):
        print("\nsetting up yard ", self.yardName)
        
        
    def yardCalcs(self):
        self.trainOut = self.rateClassification*self.fracTrainBuild/mainVar.trainSize
    
#=================================================
class roadTrainProc():
    yardName = str
    numTracks  = int
    numDest = int
    fracTrainBuild = int        #fractino of classified cars built into trains
    rateClassification = int    #num cars classified/time
    numAdjYards = int           #num adjacent yards
    adjYardNames = []
    time2AdjYards = []
    trainOut = int
    
    
    def __init__(self):
        pass
    
    def yardSetup(self):
        print("\nsetting up yard ", self.yardName)
        
        
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
        print("writing mainDictFile: ", tmpFileName, " and closing xlsx file: ", files.xlsxOutputFile)
        with open (tmpFileName, "w") as jsonFile:
            json.dump(mainDict, jsonFile)
        try:    
            xlsxWorkbook.close()
        except:
            print("\nworkbook does not exist; starting new")


#=================================================
class defFmts():
    def __init__(self):
        self.formats = {}
        from copyFormat import copy_format
        self.copy = copy_format
        
        self.formats["f1"] = xlsxWorkbook.add_format({'bold':True, 'border':2, 
            'align':'vcenter', 'font_name':'arial', 'font_size':11})
        self.formats["f2"] = xlsxWorkbook.add_format({'border':1, 'font_name':'arial', 
            'font_size':10, 'align':'center'})
        self.formats["f1_carNum"] = self.copy(xlsxWorkbook, self.formats["f1"])
        self.formats["f1_carNum"].set_align('center')
        
    def control(self):
        exclude = ["f1", "f2", "f1_carNum"]
        for name in fmtNames:
            if name in exclude:
                continue
            self.thick(name)
        return self.formats
        
        
    def shade(self, inFmt):
        self.formats[inFmt + "Shade"] = self.copy(xlsxWorkbook, self.formats[inFmt])
        self.formats[inFmt + "Shade"].set_bg_color("#D3D3D3")
        
    def thick(self, inFmt):  
        self.formats[inFmt] = self.copy(xlsxWorkbook, self.formats["f2"])
        if "left" in inFmt.lower():
            self.formats[inFmt].set_left(2)
        if "rt" in inFmt.lower():
            self.formats[inFmt].set_right(2)
        if "bot" in inFmt.lower():
            self.formats[inFmt].set_bottom(2)

        
#=================================================
class savDispDest:
    def __init__(self, destName):
        print("\nsavDispDest object created")
        self.destName = destName
        #self.oldDestName = destName
       
    def control(self):
        # test to see if new dest is OC south or OC north and shaded
        tstShade = dictProc()
        shade = tstShade.shadeTst(self.destName)
        self.savDest()
        self.dispCell(self.destName, destCol, 3, shade)
        if shade:
            self.addShade() # add shade to checkoff cells
        else: self.remShade()
        
        tstDest = self.fillStaging()
        print("tstDest: ", tstDest)
        # this block executes if next dest is staging
        if tstDest:
            self.destName = tstDest
            idxObj.mainIDX = idxObj.mainIDX + 1
            self.savDest()
            self.dispCell(self.destName, destCol, 3, False)
            # remove shade no matter b/c new dest is staging 
            self.remShade() # remove shade from checkoff cells
            
    def remShade(self):
        print("removing shaded cells")
        for idx in range(5):
            self.dispCell('', idx, 1, False)
            
    def addShade(self):
        print("adding shading to cells")
        for idx in range(5):
            self.dispCell('', idx, 1, True)

    def savDest(self):
        print("saving dest: ", self.destName, " at index: ", idxObj.mainIDX)
        #self.oldDestName = workingDict["destSet"][idxObj.mainIDX+1]
        dictProcObj = dictProc()
        dictProcObj.mainSav(idxObj.mainIDX+1, self.destName)
        destDict[self.destName] +=1
        
    def dispCell(self, text, col, wt, shade):
        print("displaying dest: ", text, " at index: ", idxObj.mainIDX)
        label = tk.Label(frames.dispCardFrame, text=text, relief=tk.RIDGE, width=wt*7)
        if shade:
            label.config(bg="darkgrey")
        label.grid(row=idxObj.mainIDX+1, column=col, sticky=tk.N+tk.S)
        label.columnconfigure(col, weight=wt)
        
        
    def fillStaging(self):
        if "east" in self.destName.lower():
            print("found eastbound dest")
            stagingDest = "East Staging"
        elif ("erie" in self.destName.lower()) and ("ble" in self.destName.lower()):
            print("found Erie RR dest")
            stagingDest = "Erie Railroad Staging"
        else: 
            print("No staging dest found")
            stagingDest = False
        return stagingDest
                    


#=================================================
def createTabs(notebook):
    for name in sheetNames:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text = name)
        tabs.append(frame)
        

#########################################################
# start of code
#########################################################

#def main():    
# Open Excel file
from fileNameSetup import fileNames
files = fileNames()
from sharedVars import frmsWind, indices, carHdr
idxObj = indices()
frames = frmsWind()

#excelFile = xlrd.open_workbook(files.excelDBFile)
#print("opened excel file: ", files.excelDBFile)

# Open sheets and populate data lists
#getCarInfo(excelFile)
# read mainDict from last save (overwrites excel file 
# contents with changes from Car_Cards)

dictObj = mainDictIO()
dictObj.readMainDictFile(files.mainDictFile)
#dictObj.createOptionlists()
if (debug):
    print("optionLists = ", optionLists)

# 
# Create root object 
# and window

editWindow = tk.Tk() 
#editWindow = tk.Toplevel(root)
editWindow.title("Car Card Selection")
# Adjust size 
editWindow.geometry( "800x600" ) 


frames.setFrms(editWindow, tk)

global tabControl
tabControl = ttk.Notebook(editWindow)
createTabs(tabControl)
rrBox = listBoxes(tabControl)

tabControl.grid(row=tabRow, column=tabCol, sticky="nw")
for idx in range(numTabs):
    createRRLists(sheetNames[idx], tabs[idx], rrBox)
    tabContents(sheetNames[idx], tabs[idx], frames)
    
setXLOutFname(fileNameEntry)

# Execute tkinter 
editWindow.mainloop()


#if __name__=="__main__":
#    main()
