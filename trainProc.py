import numpy as np
import json
from mainVars import mVars
from fileProc import readFiles


#=================================================
class trainDB():
    numTrains = 0
    numConsists = 10

    trains = {}
    consists = {}
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


  
class trainProc:      
    def trainCalcs(self, trainDict, trnName):
        from locProc import locs

        match trainDict["status"]:
            case "enroute":
                variance = np.random.normal(loc=0, scale=0.25, size=1)
                timeEnRoute = trainDict["timeEnRoute"] + mVars.prms["timeStep"] + variance
                trainDict["timeEnRoute"] = timeEnRoute
                route = trainDict["currentLoc"]
                transTime = mVars.routes[trainDict["currentLoc"]]["transTime"]
                if mVars.prms["dbgTrnProc"]: print("trainCalcs: train: ", trainDict["trainNum"], "route: ", route, 
                    ", transTime:", transTime, ", timeEnRoute: ", timeEnRoute,
                    ", variance: ", variance)
                if trainDict["timeEnRoute"] >= transTime:
                    trainDict["currentLoc"] = mVars.routes[trainDict["currentLoc"]]["dest"]
                    locs.locDat[trainDict["currentLoc"]]["trains"].append(trnName)
                    if trainDict["currentLoc"] == trainDict["finalLoc"]:
                        trainDict["status"] = "terminate"
                    else: 
                        trainDict["status"] = "dropPickup"
                    trainDict["timeEnRoute"] = 0
                    mVars.numOpBusy -=1
                    
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
