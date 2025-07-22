   
import numpy as np
import tkinter as tk
import sys
from tkinter import ttk
from stateVars import locs, trainDB, routeCls, stVarSaves
from trainProc import trainParams, trnProc
from display import dispItems
trnProcObj = trnProc()
displayObj = dispItems()
stVarObj = stVarSaves()
         
#=================================================
class mainMethods():
    
    def __init__(self):
        pass

#=================================================
    def main_loop(self):
        count = 0
        maxCount = 10
        print("mVars.time: ", mVars.time, "maxtime: ", mVars.prms["maxTime"])
        while mVars.time < mVars.prms["maxTime"]:
            stVarObj.saveStVars()
            print("\nmVars.time: ", mVars.time, ", savIDX: ", stVarSaves.savIDX)
            if mVars.wait:
                print("waiting....")
                self.step_button.wait_variable(self.var)
                self.var.set(0)
            if mVars.stepBackTrue:
                self.var.set(0)
                self.step_button.wait_variable(self.var)
                mVars.stepBackTrue = 0
                self.var.set(0)
                print("\nafter step back: mVars.time: ", mVars.time
                    , ", savIDX: ", stVarSaves.savIDX)
    
            for train in trainDB.trains:
                if mVars.time >= trainDB.trains[train]["startTime"]:
                    self.printTrainInfo(train)
                    trnProcObj.trainCalcs(trainDB.trains[train], train)
            if count == maxCount:
                print("routes: ", routeCls.routes)
                count = 0
            count +=1
            for loc in locs.locDat:
                if mVars.prms["dbgLoop"]: print ("\nAbout to process: ", 
                    loc)

                locProcObj.LocCalcs(locs.locDat, loc)
            stVarObj.incSavIDX()
            mVars.time +=1

    def printTrainInfo(self, train):
        trainStem = trainDB.trains[train]
        currentLoc = trainStem["currentLoc"]
        nextLoc = trainStem["nextLoc"]
        finalLoc = trainStem["finalLoc"]
        origLoc = trainStem["origLoc"]
        status = trainStem["status"]
        direction = trainStem["direction"]
        if mVars.prms["dbgLoop"]: print (
            "Before train processing: train: ", train, 
            "currentLoc: ", currentLoc, ", nextLoc: ", nextLoc, 
            ", origLoc: ", origLoc, 
            ", finalLoc: ", finalLoc, ", direction: ", direction,
            "status: ", status)

    def clrWait(self):
        mVars.wait = 0
        
    def quitSim(self):
        gui.root.destroy()
        sys.exit()
        #gui.root.quit()
                
    def stepBack(self):
        print("step back from ", mVars.time, " to", mVars.time-1)
        if mVars.stepBackTrue != 1:
            mVars.stepBackTrue = 1
            self.var.set(1)
        stVarObj.restStVars(1)
        displayObj.reDisp()
        mVars.time -=1
        print("waiting after step back....")
        pass

    def setupBttns(self):
        self.var = tk.IntVar()
        mVars.wait = 1
        mainLoop = tk.Button(gui.C, text="Start Sim", 
                command=lambda: self.main_loop())
        self.step_button = tk.Button(gui.C, text="Step", 
                command=lambda: self.var.set(1))
        no_wait_button = tk.Button(gui.C, text="skip wait", 
                command=lambda: self.clrWait())
        step_back_button = tk.Button(gui.C, text="Step Back", 
                command=lambda: self.stepBack())
        stVars_button = tk.Button(gui.C, text="Dump State Vars", 
                command=lambda: stVarObj.dumpStVars())
        quit_button = tk.Button(gui.C, text="Quit", 
                command=lambda: self.quitSim())
        #mainLoop.pack()
        #button1.configure(width = 10, activebackground = "#33B5E5", relief = FLAT)
        gui.C.create_window(10, 10, anchor='nw', window=mainLoop)
        gui.C.create_window(10, 60, anchor='nw', window=self.step_button)
        gui.C.create_window(10, 110, anchor='nw', window=step_back_button)
        gui.C.create_window(10, 160, anchor='nw', window=no_wait_button)
        gui.C.create_window(10, 220, anchor='nw', window=stVars_button)
        gui.C.create_window(10, 280, anchor='nw', window=quit_button)

#########################################################
# start of code
#########################################################

#def main():    
from fileProc import readFiles
files = readFiles()

from mainVars import mVars
mVars.prms = files.readFile("paramDict.txt")

#static info for each location
from layoutGeom import geom, routeGeom
from gui import gui, dispSim
layoutObj = geom()
routeGeomObj = routeGeom()
geometry = mVars.geometry = files.readFile("layoutGeomFile")
layoutObj.locListInit(geometry)
guiObj = gui()
gui.guiDict = files.readFile("guiFile")
routeGeomObj.initRoutes(geometry, gui.guiDict)


#setup initial car distribution
from carProc import carProc
carProcObj = carProc()
#carDict = files.readFile("carFile")
#carProcObj.procCarInfo(carDict)

#dynamic info for each location
from locProc import locProc
locProcObj = locProc()
locProcObj.initLocDicts()

# from gui.py
dispObj = dispSim()
dispObj.drawLayout(gui.guiDict)

# initialize dynamic action display in locations
displayObj.initLocDisp()

from startingTrains import trainFromFile
startTrainObj = trainFromFile()
startTrainObj.readTrain()

print("consists: ", trainDB.consists)

idx = 0
print("\n")
for loc in geometry:
    if mVars.prms["dbgGeom"]: print("location: ", loc,": ", geometry[loc])
    idx +=1

#setup control buttons
mainObj = mainMethods()
mainObj.setupBttns()

#gui.C.mainloop()
gui.root.mainloop()