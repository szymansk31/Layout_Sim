from shared import locs
from mainVars import mVars
from gui import gui


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
            print("ydTrains: ", ydTrains, " text: ", text)
        x = (gui.guiDict[loc]["x0"] + gui.guiDict[loc]["x1"])*0.5
        if locStem["firstDispTrn"]:
            y = gui.guiDict[loc]["y0"] + 250
            locStem["locTrnTxtID"] = \
                gui.C.create_text(x, y, text=text, width=300 , font=("Arial", 8))
            locStem["firstDispTrn"] = 0

        gui.C.itemconfigure(locStem["locTrnTxtID"], text=text, font=("Arial", 8))
            
    def drawTrain(self, train):
        from trainProc import trainDB
        from gui import gui
        #for train in trainDB.trains:
        trainDict = trainDB.trains[train]
        trainLoc = trainDict["currentLoc"]
        match trainLoc:
            case trainLoc if "route" in trainLoc:
                origLoc = trainDict["origLoc"]
                route = mVars.routes[trainLoc]
                print("draw train: ", train, "route: ", trainLoc, route)
                trnLabels = ""
                trnLabels = ' '.join(mVars.routes[trainLoc]["trains"])

                #for trainLbl in mVars.routes[trainLoc]["trains"]:
                #    trnLabels = trnLabels+"   "+trainLbl
                print("draw train: trnLabels: ", trnLabels)
                yTrn = route["yTrn"]
                trnWd = gui.guiDict["trainData"]["length"]
                trnHt = gui.guiDict["trainData"]["height"]
                xTrnTxt = route["xTrnTxt"]
                yTrnTxt = route["yTrnTxt"]
                yTrnCon = route["yTrnCon"]
                xInit = route["xTrnInit"]
                timeEnRoute = trainDict["timeEnRoute"]
                velocity = mVars.routes[trainLoc]["distPerTime"]
                print("draw train: ", train, ", timeEnRoute: ", timeEnRoute, " deltaT, distance/time: ", trainDict["deltaT"], 
                        mVars.routes[trainLoc]["distPerTime"])
                deltaX = int(trainDict["deltaT"]*velocity)
                if trainDict["direction"] == "west": deltaX = -deltaX
                
                if trainDict["timeEnRoute_Old"] == 0:
                    trainDict["xLoc"] = xInit
                    gui.C.create_rectangle(trainDict["xLoc"], yTrn, trainDict["xLoc"]+trnWd, 
                        yTrn+trnHt, fill=trainDict["color"], tags=trainDict["trnObjTag"])
                    print("train Rect obj: ", trainDict["trnObjTag"])
                    gui.C.create_text(xTrnTxt, yTrnTxt, text=trnLabels, 
                        anchor="nw", fill=trainDict["color"], tags=route["trnLabelTag"])
                else:
                    
                    trainDict["xLoc"] = trainDict["xLoc"] + deltaX
                    print("moving train by: ", deltaX)
                    print("train Rect obj: ", trainDict["trnObjTag"])

                    gui.C.move(trainDict["trnObjTag"], deltaX, 0)
                    gui.C.delete(route["trnLabelTag"])
                    gui.C.create_text(xTrnTxt, yTrnTxt, text=trnLabels, 
                        anchor="nw", fill=trainDict["color"], tags=route["trnLabelTag"])
                    
                print("draw train: ", train, ", coordinates after move: ", trainDict["xLoc"], yTrn, trainDict["xLoc"]+trnWd, yTrn+trnHt)
                print("distance via timeEnRoute: ", timeEnRoute*velocity)
                gui.C.update()
                print("train Rect obj: ", trainDict["trnObjTag"])

            case trainLoc if "route" not in trainLoc:
                pass
                                
