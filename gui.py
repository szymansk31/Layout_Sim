
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
    def __init__(self):
        gui.editWindow.title("Layout Simulation")
        # Adjust size 
        gui.editWindow.geometry( "1200x800" ) 
        gui.C.pack()
        
    def initGui(self, files):
        files.readFile("guiInfo.txt")

        
    
#=================================================
class display():
    def __init__(self):
        pass

    def drawLayout(self, guiDict):
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
                    lftObjNam = guiDict[item]["leftObj"]
                    rtObjNam = guiDict[item]["rtObj"]
                    leftEnd = guiDict[lftObjNam]["x1"]
                    rightEnd = guiDict[guiDict[item]["rtObj"]]["x0"]
                    yLoc = (guiDict[lftObjNam]["y0"]+guiDict[lftObjNam]["y1"])/2
                    xLocTxt = (guiDict[lftObjNam]["x0"]+guiDict[rtObjNam]["x1"])/2
                    tmpObj = gui.C.create_line(
                        leftEnd, yLoc, rightEnd, yLoc
                    )
                    gui.objects.append(tmpObj)
                    gui.C.create_text(
                        xLocTxt, yLoc+10,
                        text=guiDict[item]["text"]
                    )
                    


#=================================================
"""
class dispTrains():
    

"""
