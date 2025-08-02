
from fileProc import readFiles
from stateVars import trainDB, locs, routeCls
from mainVars import mVars
from trainProc import trainParams
from display import dispItems
from gui import gui

files = readFiles()

class trainFromFile():
    
    def __init__(self):
        pass
    
    def dict2TrnNam(self, train):
        self.trnName = next(iter(train))
    def dict2ConNam(self, consist):
        self.conName = next(iter(consist))
        
    def setTrnCoord(self, currLoc, dir):

        match currLoc:
            case currLoc if "route" in currLoc:
                leftObj = gui.guiDict[gui.guiDict[currLoc]["leftObj"]]
                rtObj = gui.guiDict[gui.guiDict[currLoc]["rtObj"]]
                height = leftObj["y1"] - leftObj["y0"]
                match dir:
                    case "east":
                        yTrnInit = (leftObj["y0"] + leftObj["y1"])*0.5 - height*0.25
    
    
                    case "west":
                        yTrnInit = (rtObj["y0"] + rtObj["y1"])*0.5 - height*0.25
            case currLoc:
                # if train on other than route, y for either dir is equal,
                # hence just use one loc object
                yTrnInit = (gui.guiDict[currLoc]["y0"] + gui.guiDict[currLoc]["y0"])*0.5

                        
        return yTrnInit

    def readTrain(self):
        trainProcObj = trainParams()
        trainDict = files.readFile("startingTrainFile")
        self.consistFromFile(files, "startingConsistFile")
        trainDB.consists.update(self.consist)
        for train in trainDict:
            print("\nTrain: ", train)
            currLoc = trainDict[train]["currentLoc"]
            dir = trainDict[train]["direction"]
            trainDict[train]["yTrnInit"] = self.setTrnCoord(currLoc, dir)
            trainDict[train]["color"] = trainParams.colors()
            #print("color for init train: ", trainDict[train]["color"])

            print("adding initial consist")
            trainDict[train]["trnRectTag"] = train+"RectTag"
            trainDict[train]["trnNumTag"] = train+"NumTag"
            trainDict[train]["trnLabelTag"] = train+"LabelTag"
            consistNum = trainDict[train]["consistNum"]
            consistNam = "consist"+str(consistNum)

            if "route" in currLoc:
                routeCls.routes[currLoc]["trains"].append(train)
            else: 
                locs.locDat[currLoc]["trains"].append(train)
            #self.consist[self.conName]["trainNum"] = trainDict[train]["trainNum"]
            #trainDict[train]["consistNum"] = self.consist[self.conName]["consistNum"]
            newTrain = {}
            newTrain[train] = trainDict[train]

            print("newTain dict in startingTrains: ", newTrain)
            print("with consist: ", consistNam, ", contents: ", self.consist[consistNam])
            trainDB.trains.update(newTrain)
            trainDB.trains[train]["numCars"] = trainProcObj.numCars(train)
            print("starting train: ", trainDB.trains[train])
            dispObj = dispItems()
            dispObj.drawTrain(train)
        return 

    def consistFromFile(self, files, fkey):
        self.consist = files.readFile(fkey)
        self.dict2ConNam(self.consist)
        print("\ncreating consist ", self.conName)
        #if mVars.prms["dbgTrnInit"]: print("consistDict: ", self.consist)
        return
