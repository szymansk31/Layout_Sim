
import tkinter as tk
from tkinter import Canvas
from mainVars import mVars
         
#=================================================
class gui():
    editWindow = tk.Tk() 
    C = Canvas(editWindow, height=500, width=1600, bg="lightgray")
    objects = []
    guiDict = {}
    locTextID = {}
    
    def __init__(self):
        gui.editWindow.title("Layout Simulation")
        # Adjust size 
        gui.editWindow.geometry( "1600x500" ) 
        gui.C.pack()
                

#=================================================
class dispSim():
    #trnTxtWidget = tk.Text()
    def __init__(self):
        self.trnTxtFrame = tk.Frame()
        self.trnTxtWidget = tk.Text()
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
                    #if routeCount < 2:
                    # lftObjNam = guiDict[item]["leftObj"]
                    # rtObjNam = guiDict[item]["rtObj"]
                    route = mVars.routes[item]
                    x0 = route["x0"]
                    x1 = route["x1"]
                    y0 = route["y0"]
                    y1 = route["y1"]
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
                    #self.initTrnTxtFrame(route)
                    routeCount +=1

                case "train":
                    #trainDB.trnHeight = guiDict[item]["height"]
                    #trainDB.trnLength = guiDict[item]["length"]

                    pass
        
    def initTrnTxtFrame(self, route):
        self.trnTxtWidget = tk.Text(gui.C, width=30, height=10, font=("Arial", 8), wrap="word")
        self.trnTxtFrame = gui.C.create_window(route["xTrnTxt"], route["yTrnTxt"], 
            window=self.trnTxtWidget, width=50, height=20)
        self.trnTxtWidget.insert(tk.END, "train names go here")
        return 
        #gui.trnTxtFrame.grid(row=2, column=2)
        
    def writeTrnTxt(self, text):
        print("in writeTrnTxt: text:", text)
        self.trnTxtWidget.insert(tk.END, text)

