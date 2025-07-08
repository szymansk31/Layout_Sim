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
        print("dispTrnInLoc: ydTrains: ", ydTrains, " text: ", text)
        x = (gui.guiDict[loc]["x0"] + gui.guiDict[loc]["x1"])*0.5
        y = gui.guiDict[loc]["y0"] + 250
        if locStem["firstDispTrn"]:
            locStem["locTrnTxtID"] = gui.C.create_text(x, y, text=text, width=380 , font=("Arial", 8))
            locStem["firstDispTrn"] = 0
            
        gui.C.itemconfigure(locStem["locTrnTxtID"], text=text, font=("Arial", 8))
        self.dispTrnRecs(locStem, loc, ydTrains)
     
    def dispTrnRecs(self, locStem, loc, ydtrains):
        from trainProc import trainDB
        numTrns = 0
        trnListBrkDwn = []
        trnListBuild = []
        for train in ydtrains["brkDnTrn"]: trnListBrkDwn.append(train)
        for train in ydtrains["buildTrain"]: trnListBuild.append(train)
        trainStem = trainDB.trains
        gui.C.delete(locStem["locTrnRectID"])
        trnLen = gui.guiDict["trainData"]["length"]
        trnHt = gui.guiDict["trainData"]["height"]

        totXWidth = numTrns*trnLen
        xtrn = (gui.guiDict[loc]["x0"] + gui.guiDict[loc]["x1"])*0.5 - totXWidth*0.5
        yTrnBrkDwn = gui.guiDict[loc]["y0"] - 50
        yTrnBuild = gui.guiDict[loc]["y0"] - 75

        idx = 0
        for train in trnListBrkDwn:
            #gui.C.delete(trainStem[train]["trnObjTag"])
            locStem["locTrnRectID"] = gui.C.create_rectangle(xtrn+20*idx, yTrnBrkDwn, xtrn+trnLen, 
                yTrnBrkDwn+trnHt, fill=trainStem[train]["color"])
            idx +=1
        idx = 0
        for train in trnListBuild:
            #gui.C.delete(trainStem[train]["trnObjTag"])
            locStem["locTrnRectID"] = gui.C.create_rectangle(xtrn+20*idx, yTrnBuild, xtrn+trnLen, 
                yTrnBuild+trnHt, fill=trainStem[train]["color"])
            idx +=1
                        

            
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
                    trainStem["xLoc"] = routeStem["xTrnInit"]
                    gui.C.create_rectangle(trainStem["xLoc"], yTrn, trainStem["xLoc"]+trnLen, 
                        yTrn+trnHt, fill=trainStem["color"], tags=trainStem["trnObjTag"])
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

                                
