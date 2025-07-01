import numpy as np
from time import sleep
from mainVars import mVars
from fileProc import readFiles
np.set_printoptions(precision=2, suppress=True) 


#=================================================
class trainDB():
    numTrains = 0
    numConsists = 10

    trains = {}
    consists = {}
    
    xTrain = 0.0

    def __init__(self):
        #self.trainID = int
        self.train = {}
        self.consist = {}
        self.trnName = ""
        self.conName = ""
        pass
    
    def initTrain(self):
        files = readFiles()
        self.train = files.readFile("trainFile")
        self.trnNam()

        print("adding initial consist")
        self.initConsist(files)
        self.consist[self.conName]["trainNum"] = self.train[self.trnName]["trainNum"]
        trainDB.consists.update(self.consist)
        self.train[self.trnName]["consistNum"] = self.consist[self.conName]["consistNum"]
        trainDB.trains.update(self.train)
        return 

    def initConsist(self, files):
        self.consist = files.readFile("consistFile")
        self.conNam()
        print("\ncreating consist ", self.conName)
        self.consist[self.conName]["consistNum"] = trainDB.numConsists
        trainDB.numConsists +=1
        if mVars.prms["dbgTrnInit"]: print("consistDict: ", self.consist)
        return
    
    def trnNam(self):
        self.trnName = next(iter(self.train))
    def conNam(self):
        self.conName = next(iter(self.consist))


  
class trnProc:    
  
    def __init__(self):
        self.timeEnRoute_Old = 0
        self.trainImage = any
        self.deltaT = 0.0
        
    def trainCalcs(self, trainDict, trnName):
        from locProc import locs
        from gui import gui
        match trainDict["status"]:
            case "enroute":
                variance = np.random.normal(loc=0, scale=0.25, size=1)
                self.timeEnRoute_Old = trainDict["timeEnRoute"]
                route = trainDict["currentLoc"]
                if self.timeEnRoute_Old == 0: 
                    self.drawTrain()
                    trainDB.xTrain = mVars.routes[route]["xTrnInit"]
                self.deltaT = mVars.prms["timeStep"] + variance
                
                trainDict["timeEnRoute"] = self.timeEnRoute_Old + self.deltaT
                transTime = mVars.routes[trainDict["currentLoc"]]["transTime"]
                if mVars.prms["dbgTrnProc"]: print("trainCalcs: train: ", 
                    trainDict["trainNum"], "route: ", route, 
                    ", transTime:", transTime, 
                    ", timeEnRoute: ", trainDict["timeEnRoute"], 
                    ", variance: ", variance)
                self.drawTrain()
                if trainDict["timeEnRoute"] >= transTime:
                    trainDict["currentLoc"] = mVars.routes[trainDict["currentLoc"]]["dest"]
                    locs.locDat[trainDict["currentLoc"]]["trains"].append(trnName)
                    if trainDict["currentLoc"] == trainDict["finalLoc"]:
                        trainDict["status"] = "terminate"
                    else: 
                        trainDict["status"] = "dropPickup"
                    trainDict["timeEnRoute"] = 0
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
                pass
            
    def drawTrain(self):
        from gui import gui
        for train in trainDB.trains:
            trainLoc = trainDB.trains[train]["currentLoc"]
            match trainLoc:
                case trainLoc if "route" in trainLoc:
                    origLoc = trainDB.trains[train]["origLoc"]
                    route = mVars.routes[trainLoc]
                    yTrn = route["yTrn"]
                    trnWd = route["trnWid"]
                    trnHt = route["trnHt"]
                    xTrnTxt = route["xTrnTxt"]
                    yTrnTxt = route["yTrnTxt"]
                    yTrnCon = route["yTrnCon"]
                    xInit = route["xTrnInit"]
                    print("drawTrain: deltaT, distnce/time: ", self.deltaT, mVars.routes[trainLoc]["distPerTime"])
                    deltaX = int(self.deltaT*mVars.routes[trainLoc]["distPerTime"])
                    self.xTrain += deltaX
                    print("drawTrain: coordinates: ", self.xTrain, yTrn, self.xTrain+trnWd, yTrn+trnHt)
                    if self.timeEnRoute_Old == 0:
                        self.trainImage = gui.C.create_rectangle(xInit, yTrn, xInit+trnWd, yTrn+trnHt)
                    else:
                        print("moving train by: ", deltaX)
                        gui.C.move(self.trainImage, deltaX, 0)
                        #trainImage = gui.C.create_rectangle(xTrn, yTrn, xTrn+trnWd, yTrn+trnHt)
                    #gui.C.pack()

