
import tkinter as tk
from tkinter import Canvas
from stateVars import locs, routeCls
from mainVars import mVars

#=================================================
class gui():
    root = tk.Tk() 
    C = Canvas(root, height=550, width=1600, bg="lightgray")
    #subCanvas = Canvas(root, height=100, width=100, bg="white")
    objects = []
    guiDict = {}
    locTextID = {}
    
    def __init__(self):
        gui.root.title("Layout Simulation")
        # Adjust size 
        gui.root.geometry( "1600x550" ) 
        gui.C.pack()

    def preProcGui(self):
        for loc in gui.guiDict:
            guiStem = gui.guiDict[loc]
            type = guiStem["type"]
            if type != "staging" and type != "yard" and type != "swArea": continue
            guiStem["x1"] = guiStem["x0"] + gui.guiDict["locDims"]["width"]
            guiStem["y1"] = guiStem["y0"] + gui.guiDict["locDims"]["height"]
      
        #print("new guiDict: ", gui.guiDict)

#=================================================
class dispSim():
    #trnTxtWidget = tk.Text()
    def __init__(self):
        self.trnTxtFrame = tk.Frame()
        self.trnTxtWidget = tk.Text()
        from display import dispItems
        self.displayObj = dispItems()
        pass



    def drawLayout(self, guiDict):
        routeCount = 0
        guiDict = gui.guiDict
        for item in guiDict:
            match guiDict[item]["type"]:
                case "yard"|"swArea"|"staging":
                    locStem = locs.locDat[item]
                    gui.C.create_rectangle(
                        guiDict[item]["x0"], 
                        guiDict[item]["y0"], 
                        guiDict[item]["x1"],
                        guiDict[item]["y1"],
                        fill="yellow",
                        tags=locStem["locRectID"]
                    )
                    gui.C.tag_bind(locStem["locRectID"], "<Button-1>", 
                    #    self.openTestPop("from loc Rectangle"))
                        lambda event, loc=item: self.displayObj.openLocPopup(event, loc))
                    gui.C.create_text(
                        (guiDict[item]["x0"]+guiDict[item]["x1"])/2, 
                        (guiDict[item]["y0"]+10),
                        text=guiDict[item]["text"],
                        tags=locStem["locRectID"]
                    )
                case "route":
                    #if routeCount < 2:
                    # lftObjNam = guiDict[item]["leftObj"]
                    # rtObjNam = guiDict[item]["rtObj"]
                    route = routeCls.routes[item]
                    x0 = route["x0"]
                    x1 = route["x1"]
                    y0 = route["y0"]
                    y1 = route["y1"]
                    yLoc = (y0 + y1)/2
                    xLocTxt = (x0 + x1)/2
                    gui.C.create_line(
                        x0, yLoc, x1, yLoc
                    )
                    gui.C.create_text(
                        xLocTxt, yLoc+10,
                        text=guiDict[item]["text"]
                    )
                    #self.initTrnTxtFrame(route)
                    routeCount +=1

                case "train":
                    pass
                    #trainDB.trnHeight = guiDict[item]["height"]
                    #trainDB.trnLength = guiDict[item]["length"]
                case "timer":
                    x = gui.guiDict["timer"]["x0"]
                    y = gui.guiDict["timer"]["y0"]
                    text = "time: " + str(mVars.time)
                    text += "\nmax: " + str(mVars.prms["maxTime"])
                    gui.guiDict["timer"]["timerTag"] = gui.C.create_text(
                        x, y, text=text, font=("Arial", 10)
                    )
                    pass
                case "locDims":
                    pass
        #gui.C.pack()
        #self.open_popup()
                
