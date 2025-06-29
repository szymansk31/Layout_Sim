
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
                        guiDict["x0"], 
                        guiDict["y0"], 
                        guiDict["x1"],
                        guiDict["y1"],
                        )
                    gui.objects.append(tmpObj)


#=================================================
"""
class drawTrains():
    

    route2_4 = C.create_line(200, 130, 500, 130)
    route2_4Text = C.create_text(350, 140, text="Routes 2 and 4")

    route1_3 = C.create_line(600, 130, 900, 130)
    route1_3Text = C.create_text(750, 140, text="Routes 1 and 3")

    train1Dict = {"x0": 210, "y0": 115, "width": 20, "height": 10}
    train1 = C.create_rectangle(train1Dict["x0"], train1Dict["y0"], 
            train1Dict["x0"]+train1Dict["width"],
            train1Dict["y0"]+train1Dict["height"],
            )
    train1Text = C.create_text(250, 80, text="train1", anchor="nw")
    train1_consist = C.create_text(250, 95, text="3, 1, 2, 2, 0, 0", anchor="nw")

    C.update()
    C.after(1000, lambda: C.move(train1, 50, 0))
"""
