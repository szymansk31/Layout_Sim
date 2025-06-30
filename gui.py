
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import Canvas
from mainVars import mVars
from trainProc import trainDB
from layoutGeom import geom
         
#=================================================
class gui():
    editWindow = tk.Tk() 
    C = Canvas(editWindow, height=800, width=1200, bg="yellow")
    objects = []
    guiDict = {}
    
    def __init__(self):
        gui.editWindow.title("Layout Simulation")
        # Adjust size 
        gui.editWindow.geometry( "1200x800" ) 
        gui.C.pack()
                
    
#=================================================
class dispSim():
    def __init__(self):
        pass

    def drawLayout(self, guiDict):
        routeCount = 0
        guiDict = gui.guiDict
        for item in guiDict:
            match guiDict[item]["type"]:
                case "loc":
                    tmpObj = gui.C.create_rectangle(
                        guiDict[item]["x0"], 
                        guiDict[item]["y0"], 
                        guiDict[item]["x1"],
                        guiDict[item]["y1"],
                    )
                    gui.objects.append(tmpObj)
                    gui.C.create_text(
                        (guiDict[item]["x0"]+guiDict[item]["x1"])/2, 
                        (guiDict[item]["y0"]+10),
                        text=guiDict[item]["text"]
                    )
                case "route":
                    if routeCount < 2:
                    # lftObjNam = guiDict[item]["leftObj"]
                    # rtObjNam = guiDict[item]["rtObj"]
                        x0 = mVars.routes[item]["x0"]
                        x1 = mVars.routes[item]["x1"]
                        y0 = mVars.routes[item]["y0"]
                        y1 = mVars.routes[item]["y1"]
                        yLoc = (y0 + y1)/2
                        xLocTxt = (x0 + x1)/2
                        tmpObj = gui.C.create_line(
                            x0, yLoc, x1, yLoc
                        )
                        gui.objects.append(tmpObj)
                        gui.C.create_text(
                            xLocTxt, yLoc+10,
                            text=guiDict[item]["text"]
                        )
                        routeCount +=1
                case "train":
                    pass
                    
