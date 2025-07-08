from shared import locs
from mainVars import mVars
from gui import gui
from enum import Enum


class dispObj():

    def __init__(self):
        pass
    

    def dispLocDat(self, loc):
        text = ''
        locStem = locs.locDat[loc]
        x = (gui.guiDict[loc]["x0"] + gui.guiDict[loc]["x1"])*0.5
        y = gui.guiDict[loc]["y0"] + 120

        for track in locStem["tracks"]:
            text += track + "\n"
            text += str(locStem["tracks"][track]) + "\n"
        if locStem["firstDispLoc"]:
            locStem["locObjID"] = \
                gui.C.create_text(x, y, text=text, font=("Arial", 8))
                
        gui.C.itemconfigure(locStem["locObjID"], text=text, font=("Arial", 8))
        locStem["firstDispLoc"] = 0
        pass

    def dispTrnInLoc(self, loc, ydTrains):
        from trainProc import trainDB
        locStem = locs.locDat[loc]
        trainStem = trainDB.trains
        text = loc + "\n"
        numTrns = 0
        #if not locStem["trains"]:
        for train in locStem["trains"]:

            consistNum = trainStem[train]["consistNum"]
            consistNam = "consist"+str(consistNum)
            for action in ydTrains:
                if train in ydTrains[action]:
                    text += train + ": " + action + "\n"
            #text += train+"\n"
            text += str(trainDB.consists[consistNam]["stops"]) 
            text += "\n"
            numTrns +=1
        print("dispTrnInLoc: ydTrains: ", ydTrains, " text: ", text)
        x = (gui.guiDict[loc]["x0"] + gui.guiDict[loc]["x1"])*0.5
        y = gui.guiDict[loc]["y0"] + 250
        if locStem["firstDispTrnTxt"]:
            locStem["locTrnTxtID"] = gui.C.create_text(x, y, text=text, width=380 , font=("Arial", 8))
            
        gui.C.itemconfigure(locStem["locTrnTxtID"], text=text, font=("Arial", 8))
        self.dispTrnRecs(locStem, loc, ydTrains, numTrns)
        
    def dispTrnRecs(self, locStem, loc, ydtrains, numTrns):
        from trainProc import trainDB
        
        dispList = {
            "actions": {
            "brkDnTrn": {"trains": [], 
                "y": gui.guiDict[loc]["y0"] - 30,},
            "buildTrain": {"trains": [],
                "y": gui.guiDict[loc]["y0"] - 55}},
            
            "allTrains": {"trains": [], "y": 0,}
            
            }
        for action in dispList["actions"]:
            for train in ydtrains[action]:
                dispList["actions"][action]["trains"].append(train)
                dispList["allTrains"]["trains"].append(train)
            
        trainStem = trainDB.trains
        trnLen = gui.guiDict["trainData"]["length"]
        trnHt = gui.guiDict["trainData"]["height"]

        totXWidth = numTrns*trnLen
        xtrn = (gui.guiDict[loc]["x0"] + gui.guiDict[loc]["x1"])*0.5 - totXWidth*0.5

        gui.C.delete(locStem["locTrnRectID"])
        for action in dispList["actions"]:
            idx = 0
            actionStem = dispList["actions"][action]
            y = actionStem["y"]
            if locStem["firstDispTrnTxt"]:
                gui.C.create_text(xtrn-50, y+6, text=action, 
                        font=("Arial", 8))
            for train in actionStem["trains"]:
                trainNum = train[5:]
                gui.C.delete(trainStem[train]["trnObjTag"])
                gui.C.create_rectangle(xtrn+20*idx, y, xtrn+20*idx+trnLen, 
                    y+trnHt, fill=trainStem[train]["color"], 
                    tags=locStem["locTrnRectID"])
                gui.C.create_text(xtrn+10+20*idx, y+6, text=trainNum , 
                    font=("Arial", 8), tags=locStem["locTrnRectID"])
                idx +=1
        locStem["firstDispTrnTxt"] = 0

            
    def drawTrain(self, train):
        from trainProc import trainDB
        from gui import gui

        trainStem = trainDB.trains[train]
        trainLoc = trainStem["currentLoc"]
        
        trnLen = gui.guiDict["trainData"]["length"]
        trnHt = gui.guiDict["trainData"]["height"]
        match trainLoc:
            case trainLoc if "route" in trainLoc:
                routeStem = mVars.routes[trainLoc]
                yTrn = routeStem["yTrn"]
                xTrnTxt = routeStem["xTrnTxt"]
                yTrnTxt = routeStem["yTrnTxt"]
                timeEnRoute = trainStem["timeEnRoute"]
                velocity = routeStem["distPerTime"]
                print("draw train: ", train, "route: ", trainLoc, routeStem)
                trnLabels = ""
                trnLabels = ' '.join(routeStem["trains"])

                print("draw train: trnLabels: ", trnLabels)
                print("draw train: ", train, ", timeEnRoute: ", timeEnRoute, " deltaT, distance/time: ", trainStem["deltaT"], 
                        routeStem["distPerTime"])
                deltaX = int(trainStem["deltaT"]*velocity)
                if trainStem["direction"] == "west": deltaX = -deltaX
                
                if trainStem["firstDispTrn"] == 1:
                    trainStem["xLoc"] = trainStem["xTrnInit"]
                    trainNum = train[5:]

                    gui.C.create_rectangle(trainStem["xLoc"], yTrn, trainStem["xLoc"]+trnLen, 
                        yTrn+trnHt, fill=trainStem["color"], tags=trainStem["trnObjTag"])
                    gui.C.create_text(trainStem["xLoc"]+10, yTrn+6, text=trainNum , 
                        font=("Arial", 8), tags=trainStem["trnObjTag"])

                    #print("train Rect obj: ", trainStem["trnObjTag"])
                    gui.C.create_text(xTrnTxt, yTrnTxt, text=trnLabels, 
                        anchor="nw", fill=trainStem["color"], tags=routeStem["trnLabelTag"])
                    trainStem["firstDispTrn"] = 0
                    
                else:
                    trainStem["xLoc"] = trainStem["xLoc"] + deltaX
                    print("moving train by: ", deltaX)
                    print("train Rect obj: ", trainStem["trnObjTag"])
                    
                    gui.C.move(trainStem["trnObjTag"], deltaX, 0)
                    gui.C.itemconfigure(routeStem["trnLabelTag"], text=trnLabels, 
                        anchor="nw", fill=trainStem["color"])
                    
                print("draw train: ", train, ", coordinates after move: ", trainStem["xLoc"], yTrn, trainStem["xLoc"]+trnLen, yTrn+trnHt)
                print("distance via timeEnRoute: ", timeEnRoute*velocity)
                gui.C.update()
                #print("train Rect obj: ", trainStem["trnObjTag"])

            case trainLoc if "route" not in trainLoc:
                pass
            
            case trainloc if "xyz" in trainloc:
                gui.C.delete(trainStem["trnObjTag"])
                xtrn = (gui.guiDict[trainLoc]["x0"] + gui.guiDict[trainLoc]["x1"])*0.5 - trnLen
                yTrn = gui.guiDict[trainLoc]["y0"] - 50
                if (trainStem["status"] == "terminate") or (trainStem["status"] == "dropPickup"):
                    gui.C.create_rectangle(xtrn, yTrn, xtrn+trnLen, 
                    yTrn+trnHt, fill=trainStem["color"], tags=trainStem["trnObjTag"])

                                
