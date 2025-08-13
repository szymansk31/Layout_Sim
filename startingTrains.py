
from fileProc import readFiles
from stateVars import trainDB, locs, routeCls
from mainVars import mVars
from trainInit import trainInit
from display import dispItems
from gui import gui
from coords import transForms
from locProc import locProc, locBase
from dispatch import rtCaps

files = readFiles()

class trainFromFile():
    
    def __init__(self):
        pass
    
    def dict2TrnNam(self, train):
        self.trnName = next(iter(train))
    def dict2ConNam(self, consist):
        self.conName = next(iter(consist))
        
    def readTrain(self):
        trainInitObj = trainInit()
        coordObj = transForms()
        locProcObj = locProc()
        rtCapsObj = rtCaps()
        trainDict = files.readFile("startingTrainFile")
        self.consistFromFile(files, "startingConsistFile")
        trainDB.consists.update(self.consist)
        for train in trainDict:
            print("\nTrain: ", train)
            trainDB.strtTrns.append(train)
            currLoc = trainDict[train]["currentLoc"]

            trainDict[train]["color"] = trainInit.colors()
            #print("color for init train: ", trainDict[train]["color"])

            print("adding initial consist")
            trainDict[train]["trnRectTag"] = train+"RectTag"
            trainDict[train]["trnNumTag"] = train+"NumTag"
            trainDict[train]["trnLabelTag"] = train+"LabelTag"
            consistNum = trainDict[train]["consistNum"]
            consistNam = "consist"+str(consistNum)

            if "route" in currLoc:
                locProcObj.setTrnCoord(currLoc, trainDict[train])
            #self.consist[self.conName]["trainNum"] = trainDict[train]["trainNum"]
            #trainDict[train]["consistNum"] = self.consist[self.conName]["consistNum"]
            newTrain = {}
            newTrain[train] = trainDict[train]

            print("newTain dict in startingTrains: ", newTrain)
            print("with consist: ", consistNam, ", contents: ", self.consist[consistNam])
            trainDB.trains.update(newTrain)
            trainDB.trains[train]["numCars"] = trainInitObj.numCars(train)

            if "route" in currLoc:
                #routeCls.routes[currLoc]["trains"].append(train)
                rtCapsObj.fillTrnsOnRoute(currLoc, train)
                # fill trainDB with xPlot and yPlot, the canvas/screen coords
                coordObj.xRoute2xPlot(currLoc, train)
                #trainDB.trains[train]["coord"]["yPlot"] -= gui.guiDict["locDims"]["height"]*0.25
            else: 
                locBase.addTrn2Loc_rt(currLoc, train)
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
