   
import numpy as np
import tkinter as tk
from tkinter import ttk
from stateVars import locs, trainDB, routeCls, stVarSaves
from trainProc import trainParams, trnProc
trnProcObj = trnProc()
stVarObj = stVarSaves()
         
#=================================================
def main_loop():

    print("mVars.time: ", mVars.time, "maxtime: ", mVars.prms["maxTime"])
    while mVars.time < mVars.prms["maxTime"]:
        print("\nmVars.time: ", mVars.time)
        if mVars.wait:
            print("waiting....")
            step_button.wait_variable(var)
            var.set(0)
        if mVars.stepBackTrue:
            var.set(0)
            step_button.wait_variable(var)
            mVars.stepBackTrue = 0
            var.set(0)
            
        for train in trainDB.trains:
            printTrainInfo(train)
            if mVars.time > trainDB.trains[train]["startTime"]:
                trnProcObj.trainCalcs(trainDB.trains[train], train)

        for loc in locs.locDat:
            if mVars.prms["dbgLoop"]: print ("\nAbout to process: ", 
                loc)

            locProcObj.LocCalcs(locs.locDat, loc)
        stVarObj.saveStVars()
        mVars.time +=1

def printTrainInfo(train):
    trainStem = trainDB.trains[train]
    currentLoc = trainStem["currentLoc"]
    finalLoc = trainStem["finalLoc"]
    origLoc = trainStem["origLoc"]
    status = trainStem["status"]
    direction = trainStem["direction"]
    if mVars.prms["dbgLoop"]: print ("Before train processing: train: ", 
        train, "currentLoc: ", currentLoc, ", origLoc: ", origLoc, 
        ", finalLoc: ", finalLoc, ", direction: ", direction,
        "status: ", status)

def clrWait():
    mVars.wait = 0
            
def stepBack():
    print("step back from ", mVars.time, " to", mVars.time-1)
    if mVars.stepBackTrue != 1:
        mVars.stepBackTrue = 1
        var.set(1)
    mVars.time -=1
    print("waiting....")
    pass

#########################################################
# start of code
#########################################################

#def main():    
from fileProc import readFiles
files = readFiles()

from mainVars import mVars
mVars.prms = files.readFile("paramFile")

from layoutGeom import geom, routeGeom
from gui import gui, dispSim
layoutObj = geom()
routeGeomObj = routeGeom()
geometry = mVars.geometry = files.readFile("layoutGeomFile")
layoutObj.locListInit(geometry)
guiObj = gui()
gui.guiDict = files.readFile("guiFile")
routeCls.routes = routeGeomObj.initRoutes(geometry, gui.guiDict)


#setup initial car distribution
from carProc import carProc
carProcObj = carProc()
carDict = files.readFile("carFile")
carProcObj.procCarInfo(carDict)

from locProc import locProc
locProcObj = locProc()
locProcObj.initLocDicts()

from startingTrains import trainFromFile
startTrainObj = trainFromFile()
startTrainObj.readTrain()

print("consists: ", trainDB.consists)

# from gui.py
dispObj = dispSim()
dispObj.drawLayout(gui.guiDict)

idx = 0
print("\n")
for loc in geometry:
    if mVars.prms["dbgGeom"]: print("location: ", loc,": ", geometry[loc])
    idx +=1

#main loop:
var = tk.IntVar()
mVars.wait = 1
mainLoop = tk.Button(gui.C, text="Start Sim", 
        command=lambda: main_loop())
step_button = tk.Button(gui.C, text="Step", 
        command=lambda: var.set(1))
no_wait_button = tk.Button(gui.C, text="skip wait", 
        command=lambda: clrWait())
step_back_button = tk.Button(gui.C, text="Step Back", 
        command=lambda: stepBack())
mainLoop.pack()
#button1.configure(width = 10, activebackground = "#33B5E5", relief = FLAT)
button_window = gui.C.create_window(10, 10, anchor='nw', window=mainLoop)
button_window = gui.C.create_window(10, 60, anchor='nw', window=step_button)
button_window = gui.C.create_window(10, 110, anchor='nw', window=step_back_button)
button_window = gui.C.create_window(10, 160, anchor='nw', window=no_wait_button)

#gui.editWindow.after(300, main_loop())

gui.C.mainloop()