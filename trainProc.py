import numpy as np
from time import sleep
import tkinter as tk
from mainVars import mVars
from fileProc import readFiles
np.set_printoptions(precision=2, suppress=True) 


#=================================================
class trainDB():
    numTrains = 1
    numConsists = 10

    trains = {}
    consists = {}
    trnHeight = 10
    trnLength = 20
    colorIDX = 0
    colorList = ["red", "green", "yellow", "orange", "purple", "blue"]


    def __init__(self):
        #self.trainID = int
        self.train = {}
        self.consist = {}
        self.trnName = ""
        self.conName = ""
        pass
    
    @classmethod
    def colors(cls):
        maxColorIDX = 5
        cls.color = cls.colorList[cls.colorIDX]
        cls.colorIDX +=1
        if cls.colorIDX == maxColorIDX: cls.colorIDX = 0
        print("color: ", cls.color)
        return cls.color
        
    def initTrain(self):
        files = readFiles()
        self.train = files.readFile("trainFile")
        self.dict2TrnNam(self.train)
        self.train[self.trnName]["color"] = trainDB.colors()
        print("color for init train: ", self.train[self.trnName]["color"])

        print("adding initial consist")
        self.initConsist(files, "consistFile")
        self.conName
        tmpLoc = self.train[self.trnName]["currentLoc"]
        if "route" in tmpLoc:
            mVars.routes[tmpLoc]["trains"].append(self.trnName)
        self.consist[self.conName]["trainNum"] = self.train[self.trnName]["trainNum"]
        trainDB.consists.update(self.consist)
        self.train[self.trnName]["consistNum"] = self.consist[self.conName]["consistNum"]
        trainDB.trains.update(self.train)
        return 

    def initConsist(self, files, fkey):
        self.consist = files.readFile(fkey)
        self.dict2ConNam(self.consist)
        print("\ncreating consist ", self.conName)
        self.consist[self.conName]["consistNum"] = trainDB.numConsists
        trainDB.numConsists +=1
        if mVars.prms["dbgTrnInit"]: print("consistDict: ", self.consist)
        return
    
    def dict2TrnNam(self, train):
        self.trnName = next(iter(train))
    def dict2ConNam(self, consist):
        self.conName = next(iter(consist))
        
    def newTrain(self):
        newTrainNum = trainDB.numTrains+1
        newTrainNam = "train"+str(newTrainNum)
        newConsistNum = trainDB.numConsists+1 
        newConsistNam = "consist"+str(newConsistNum)
        
        trainDB.trains.update(
        {
        newTrainNam: {
            "trainNum": newTrainNum,
            "consistNum": newConsistNum,
            "numCars": 0,
            "status": "",
            "origLoc": "",
            "finalLoc": "",
            "currentLoc": "",
            "xLoc": 0,
            "timeEnRoute": 0,
            "timeEnRoute_Old": 0,
            "deltaT": 0,
            "objID": 0,
            "firstDisp": 1,
            "numStops": 0,
            "stops": [
                ],
            "color": "",
            "locoType": "2-8-0"}
        })
        self.newConsist(newConsistNum, newTrainNum)
        trainDB.numTrains +=1
        trainDB.numConsists +=1
        return newTrainNam, newConsistNam
    
    def newConsist(self, newConsistNum, newTrainNum):
        newConNam = "consist"+str(newConsistNum)
        trainDB.consists.update(
        {
        newConNam: {
            "consistNum": newConsistNum,
            "trainNum": newTrainNum,
            "stops": {
                "yard"   :{"box": 0, "tank": 0,"rfr": 0, "hop": 0, 
                    "gons": 0, "flats": 0, "psgr": 0},
            },
            "numBox": 0,
            "numTank": 0,
            "numReefer": 0,
            "numHopper": 0,
            "numGon": 0,
            "numFlat": 0,
            "numPsgr": 0}
        })
        return 


  
class trnProc:    
  
    def __init__(self):
        self.timeEnRoute_Old = 0
        self.trainImage = any
        self.deltaT = 0.0
        from gui import gui, dispSim
        self.dispObj = dispSim()



    def trainCalcs(self, trainDict, trnName):
        from locProc import locs
        from gui import gui
        match trainDict["status"]:
            case "enroute":
                variance = np.random.normal(loc=0, scale=0.25, size=1)
                trainDict["timeEnRoute_Old"] = trainDict["timeEnRoute"]
                routeNam = trainDict["currentLoc"]
                routeStem = mVars.routes[routeNam]
                if trainDict["timeEnRoute_Old"] == 0: 
                    self.drawTrain()
                trainDict["deltaT"] = mVars.prms["timeStep"] + variance
                
                trainDict["timeEnRoute"] = trainDict["timeEnRoute_Old"] + trainDict["deltaT"]
                transTime = mVars.routes[trainDict["currentLoc"]]["transTime"]
                if mVars.prms["dbgTrnProc"]: print("trainCalcs: train: ", 
                    trainDict["trainNum"], "route: ", routeNam, 
                    ", origin: ", trainDict["origLoc"], ", dest:", trainDict["finalLoc"], 
                    ", direction: ", routeStem["direction"], ", transTime:", transTime, 
                    ", timeEnRoute: ", trainDict["timeEnRoute"], 
                    ", variance: ", variance)
                self.drawTrain()
                if trainDict["timeEnRoute"] >= transTime:
                    #remove train from that route
                    index = mVars.routes[routeNam]["trains"].index(trnName)
                    mVars.routes[routeNam]["trains"].pop(index)
                    gui.C.delete(routeStem["trnLabelTag"])
        
                    trainDict["currentLoc"] = routeStem["dest"]
                    locs.locDat[trainDict["currentLoc"]]["trains"].append(trnName)
                    if trainDict["currentLoc"] == trainDict["finalLoc"]:
                        trainDict["status"] = "terminate"
                    else: 
                        trainDict["status"] = "dropPickup"
                    trainDict["timeEnRoute"] = 0
                    print("train: ", trnName, "trainDict: ", trainDict)
                    mVars.numOpBusy -=1
                    #trainObj.initTrain()
                    
            case "building":
                pass
            case "terminate":
                pass
            case "dropPickup":
                if "sw" in trainDict["currentLoc"]:   
                    pass
                else: 
                    pass
                pass
            case "ready2Leave":
                trainDict["status"] = "enroute"
                self.drawTrain()
                pass
            
    def drawTrain(self):
        from gui import gui, dispSim
        for train in trainDB.trains:
            trainDict = trainDB.trains[train]
            trainLoc = trainDict["currentLoc"]
            match trainLoc:
                case trainLoc if "route" in trainLoc:
                    origLoc = trainDict["origLoc"]
                    route = mVars.routes[trainLoc]
                    trnLabels = ""
                    for trainLbl in mVars.routes[trainLoc]["trains"]:
                        trnLabels = trnLabels+"   "+trainLbl
                    yTrn = route["yTrn"]
                    trnWd = trainDB.trnLength
                    trnHt = trainDB.trnHeight
                    xTrnTxt = route["xTrnTxt"]
                    yTrnTxt = route["yTrnTxt"]
                    yTrnCon = route["yTrnCon"]
                    xInit = route["xTrnInit"]
                    print("drawTrain: deltaT, distance/time: ", trainDict["deltaT"], mVars.routes[trainLoc]["distPerTime"])
                    deltaX = int(trainDict["deltaT"]*mVars.routes[trainLoc]["distPerTime"])
                    if route["direction"] == "west": deltaX = -deltaX
                    
                    print("drawTrain: coordinates: ", trainDict["xLoc"], yTrn, trainDict["xLoc"]+trnWd, yTrn+trnHt)
                    if trainDict["timeEnRoute_Old"] == 0:
                        trainDict["xLoc"] = xInit
                        trainDict["objID"] = gui.C.create_rectangle(trainDict["xLoc"], yTrn, trainDict["xLoc"]+trnWd, yTrn+trnHt, fill=trainDict["color"])
                        gui.C.create_text(xTrnTxt, yTrnTxt, text=trnLabels, anchor="nw", fill=trainDict["color"], tags=route["trnLabelTag"])
                    else:
                        
                        trainDict["xLoc"] = trainDict["xLoc"] + deltaX
                        print("moving train by: ", deltaX)
                        gui.C.move(trainDict["objID"], deltaX, 0)
                        gui.C.delete(route["trnLabelTag"])
                        gui.C.create_text(xTrnTxt, yTrnTxt, text=trnLabels, anchor="nw", fill=trainDict["color"], tags=route["trnLabelTag"])
                    gui.C.update()
                case trainLoc if "route" not in trainLoc:
                    pass
                                

