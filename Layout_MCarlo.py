   
import numpy as np
import tkinter as tk
from tkinter import ttk
         
#=================================================
def main_loop():
    count = 0
    maxCount = 7

    print("mVars.time: ", mVars.time, "maxtime: ", mVars.prms["maxTime"])
    while mVars.time < mVars.prms["maxTime"]:
        print("\nmVars.time: ", mVars.time)
        for train in trainDB.trains:
            currentLoc = trainDB.trains[train]["currentLoc"]
            status = trainDB.trains[train]["status"]
            if mVars.prms["dbgLoop"]: print ("Before train processing: train: ", 
                train, "currentLoc: ", currentLoc, "status: ", status)
            trnProcObj.trainCalcs(trainDB.trains[train], train)
        count +=1
        if mVars.wait:
            print("waiting....")
            wait_button.wait_variable(var)
            var.set(0)
        for loc in geometry:
            if mVars.prms["dbgLoop"]: print ("\nBefore loc processing: loop var: ", 
                loc, "currentLoc: ", currentLoc)

            ydProcObj.yardCalcs(geometry, loc)
        mVars.time +=1

def clrWait():
    mVars.wait = 0
            

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
mVars.routes = routeGeomObj.initRoutes(geometry, gui.guiDict)


#setup initial car distribution
from carProc import carProc
carProcObj = carProc()
carDict = files.readFile("carFile")
carProcObj.procCarInfo(carDict)

from locProc import locProc
ydProcObj = locProc()
from trainProc import trnProc, trainDB
trnProcObj = trnProc()
trains = trainDB()
trains.initTrain()

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
wait_button = tk.Button(gui.C, text="Continue", 
        command=lambda: var.set(1))
no_wait_button = tk.Button(gui.C, text="skip wait", 
        command=lambda: clrWait())
mainLoop.pack()
#button1.configure(width = 10, activebackground = "#33B5E5", relief = FLAT)
button_window = gui.C.create_window(10, 10, anchor='nw', window=mainLoop)
button_window = gui.C.create_window(100, 10, anchor='nw', window=wait_button)
button_window = gui.C.create_window(190, 10, anchor='nw', window=no_wait_button)

#gui.editWindow.after(300, main_loop())

gui.C.mainloop()