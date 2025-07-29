
import tkinter as tk
from tkinter import Canvas
import sys

from mainVars import mVars
from gui import gui
from stateVars import locs, trainDB, routeCls


class dispItems():

    def __init__(self):
        pass
    
    def initLocDisp(self):
        for loc in locs.locDat:
            x = (gui.guiDict[loc]["x0"] + gui.guiDict[loc]["x1"])*0.5
            y = gui.guiDict[loc]["y0"] + 45
            text = "action: "
            locs.locDat[loc]["actionObjID"] = \
                gui.C.create_text(x, y, text=text, font=("Arial", 8))
            
            type = locs.locDat[loc]["type"]
            if type == "yard" or type == "swArea":
                self.openLocPopup(0, loc)
            #locs.locPop = {}

    def openLocPopup(self, event, loc):
        # Create a Toplevel window for the popup
        locs.locPop[loc] = tk.Toplevel(gui.root)
        print("popup windows: ", locs.locPop)
        locs.locPop[loc].title(loc + " Window")
        locs.locPop[loc].geometry("400x400")
        locs.locPop[loc]['bg'] = 'tan'
        
        type = locs.locDat[loc]["type"]
        text = tk.StringVar()
        text = loc + "\n"
        locStem = locs.locDat[loc]
        match type:
            case "yard":
                for track in locStem["tracks"]:
                    text += track + "\n"
                    text += str(locStem["tracks"][track]) + "\n"
            case "swArea":
                indusStem = locStem["industries"]
                for indus in indusStem:
                    text += indus + ":\n"
                    tmpList = [carStatus+str(indusStem[indus][carStatus])\
                        for carStatus in indusStem[indus]\
                        if "numCarS" not in carStatus ]
                    #gen = (carStatus for carStatus in indusStem[indus]\
                    #    if "numCarS" not in carStatus)
                    #for carStatus in gen:
                    text += "\n".join(tmpList) + "\n"
                
        locs.labels[loc] = tk.Label(locs.locPop[loc], text=text)
        print("just wrote label; label obj is: ", locs.labels[loc])
        locs.labels[loc].config(font=("Arial", 8), justify="left")
        locs.labels[loc].pack()

    def reDisp(self):
        for loc in locs.locDat:
            self.dispTrnLocDat(loc)
            
        for train in trainDB.trains:
            self.drawTrain(train)

    def updateTimer(self):
        text = "time: " + str(mVars.time)
        text += "\nmax: " + str(mVars.prms["maxTime"])
        gui.C.itemconfigure(gui.guiDict["timer"]["timerTag"], 
            text=text, font=("Arial", 10))


    def dispTrnLocDat(self, loc):
        text = ''
        type = locs.locDat[loc]["type"]
        locStem = locs.locDat[loc]
        trainStem = trainDB.trains
        ydTrains = trainDB.ydTrains
        numTrns = 0
        x = (gui.guiDict[loc]["x0"] + gui.guiDict[loc]["x1"])*0.5
        y = gui.guiDict[loc]["y0"] + 300
        
        match type:
            case "yard":
                text = loc + ": yard tracks: \n"
                for track in locStem["tracks"]:
                    text += track + "\n"
                    text += str(locStem["tracks"][track]) + "\n"
                text += "\nTrains worked in yard\n"
            case "swArea":
                indusStem = locStem["industries"]
                text = loc + ": industries: \n"
                for indus in indusStem:
                    text += indus + ":\n"
                    tmpList = [carStatus+" "+str(indusStem[indus][carStatus])\
                        for carStatus in indusStem[indus]\
                        if "numCarS" not in carStatus ]
                    text += "\n".join(tmpList) + "\n"
                text += "\nTrains in this area:\n"
        for train in locStem["trains"]:
            consistNum = trainStem[train]["consistNum"]
            consistNam = "consist"+str(consistNum)
            for action in ydTrains:
                if train in ydTrains[action]:
                    text += train + ": " + action + "\n"
            #text += train+"\n"
            for stop in trainDB.consists[consistNam]["stops"]:
                text += stop+": "+str(trainDB.consists[consistNam]["stops"][stop]) 
                text += "\n"
            numTrns +=1
        if locStem["firstDispLoc"]:
            locStem["locObjID"] = \
                gui.C.create_text(x, y, text=text, font=("Arial", 8), justify="left")
            locStem["firstDispLoc"] = 0

        if loc in locs.labels:
            locs.labels[loc].config(text=text)
            gui.C.delete(locStem["locTrnTxtID"])
            gui.C.delete(locStem["locObjID"])
        else:
            gui.C.itemconfigure(locStem["locObjID"], text=text, font=("Arial", 8))

        self.dispTrnRecs(locStem, loc, ydTrains, numTrns)

    
    def dispActionDat(self, loc, action, ydTrainNam):
        text = ''
        locStem = locs.locDat[loc]

        text = "action:" + action + " \n" + \
            ydTrainNam 
        gui.C.itemconfigure(locStem["actionObjID"], text=text, font=("Arial", 8))
        pass

    def dispSwitchDat(self, loc, indus, ydTrainNam):
        text = ''
        locStem = locs.locDat[loc]

        text = ydTrainNam + " switching:\n" + indus
        gui.C.itemconfigure(locStem["actionObjID"], text=text, font=("Arial", 8))
        pass

        
    def dispTrnRecs(self, locStem, loc, ydtrains, numTrns):        
        actionIter = iter(trainDB.ydTrains)
        action1 = next(actionIter)
        action2 = next(actionIter)

        y0 = gui.guiDict[loc]["y0"]
        dispList = {
            "actions": {
            action1: {"trains": [], 
                "y": y0 - 55,},
            action2: {"trains": [],
                "y": y0 - 40}}
            }
        
        for action in dispList["actions"]:
            for train in ydtrains[action]:
                dispList["actions"][action]["trains"].append(train)

        dispList["actions"]["ready2Leave"] = dict(trains= [], y= y0 - 25)
        dispList["actions"]["built"] = dict(trains = [], y = y0 - 10)
        tmp = locs.locDat[loc]["trains"]
        for train in tmp:
            if trainDB.trains[train]["status"] == "ready2Leave":
                dispList["actions"]["ready2Leave"]["trains"].append(train)
            if trainDB.trains[train]["status"] == "built":
                dispList["actions"]["built"]["trains"].append(train)
        print("dispList: ", dispList)
        trainStem = trainDB.trains
        trnLen = gui.guiDict["trainData"]["length"]
        trnHt = gui.guiDict["trainData"]["height"]

        totXWidth = numTrns*trnLen
        xtrn = (gui.guiDict[loc]["x0"] + gui.guiDict[loc]["x1"])*0.5 - totXWidth*0.5

        gui.C.delete(locStem["locTrnRectID"])
        gui.C.delete(locStem["locTrnNumID"])
        for action in dispList["actions"]:
            idx = 0
            actionStem = dispList["actions"][action]
            y = actionStem["y"]
            if locStem["firstDispTrnTxt"]:
                gui.C.create_text(xtrn-90, y+6, text=action, 
                        font=("Arial", 8))
            for train in actionStem["trains"]:
                trainNum = train[5:]
                gui.C.delete(trainStem[train]["trnRectTag"])
                gui.C.delete(trainStem[train]["trnNumTag"])
                gui.C.create_rectangle(xtrn+20*idx, y, xtrn+20*idx+trnLen, 
                    y+trnHt, fill=trainStem[train]["color"], 
                    tags=locStem["locTrnRectID"])
                gui.C.create_text(xtrn+10+20*idx, y+6, text=trainNum , 
                    font=("Arial", 8), tags=locStem["locTrnNumID"])
                idx +=1
        locStem["firstDispTrnTxt"] = 0

            
    def drawTrain(self, train):
        print("drawTrain called by: ", sys._getframe(1).f_code.co_name)

        trainStem = trainDB.trains[train]
        trainLoc = trainStem["currentLoc"]
        
        trnLen = gui.guiDict["trainData"]["length"]
        trnHt = gui.guiDict["trainData"]["height"]
        match trainLoc:
            case trainLoc if "route" in trainLoc:
                routeStem = routeCls.routes[trainLoc]
                yTrn = routeStem["yTrn"]
                xTrnTxt = routeStem["xTrnTxt"]
                yTrnTxt = routeStem["yTrnTxt"]
                timeEnRoute = trainStem["timeEnRoute"]
                velocity = routeStem["distPerTime"]
                print("draw train: ", train, "currentLoc: ", trainLoc, ", trainDict: ", trainStem)

                print("draw train: ", train, ", timeEnRoute: ", timeEnRoute, " deltaT, distance/time: ", trainStem["deltaT"], 
                        routeStem["distPerTime"])
                deltaX = int(trainStem["deltaT"]*velocity)
                if trainStem["direction"] == "west": deltaX = -deltaX
                
                if trainStem["firstDispTrn"] == 1:
                    trainStem["xLoc"] = trainStem["xTrnInit"]
                    trainNum = train[5:]
                    
                    gui.C.delete(trainStem["trnRectTag"])
                    gui.C.delete(trainStem["trnNumTag"])

                    gui.C.create_rectangle(trainStem["xLoc"], yTrn, trainStem["xLoc"]+trnLen, 
                        yTrn+trnHt, fill=trainStem["color"], tags=trainStem["trnRectTag"])
                    gui.C.create_text(trainStem["xLoc"]+10, yTrn+6, text=trainNum , 
                        font=("Arial", 8), tags=trainStem["trnNumTag"])

                    #print("train Rect obj: ", trainStem["trnObjTag"])
                    #gui.C.create_text(xTrnTxt, yTrnTxt, text=trnLabels, 
                    #    anchor="nw", fill=trainStem["color"], tags=routeStem["trnLabelTag"])
                    trainStem["firstDispTrn"] = 0
                    
                else:
                    trainStem["xLoc"] = trainStem["xLoc"] + deltaX
                    print("moving train by: ", deltaX)
                    
                    #gui.C.delete(trainStem["trnRectTag"])
                    #gui.C.delete(trainStem["trnNumTag"])
                    #gui.C.move(trainStem["trnObjTag"], deltaX, 0)
                    gui.C.coords(trainStem["trnRectTag"], trainStem["xLoc"], yTrn, trainStem["xLoc"]+trnLen, 
                        yTrn+trnHt)
                    gui.C.coords(trainStem["trnNumTag"], trainStem["xLoc"]+10, yTrn+6)
                    #gui.C.itemconfigure(routeStem["trnLabelTag"], text=trnLabels, 
                    #    anchor="nw", fill=trainStem["color"])
                    
                print("draw train: ", train, ", coordinates after move: ", trainStem["xLoc"], yTrn, trainStem["xLoc"]+trnLen, yTrn+trnHt)
                print("distance via timeEnRoute: ", timeEnRoute*velocity)
                gui.C.update()

            case trainLoc if "route" not in trainLoc:
                pass
            
                                
