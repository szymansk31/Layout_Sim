import numpy as np
import tkinter as tk
from mainVars import mVars
from fileProc import readFiles
from display import dispObj
np.set_printoptions(precision=2, suppress=True) 


#=================================================
class trainDB():
    numTrains = 0
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
        self.files = readFiles()

        pass
    
    @classmethod
    def colors(cls):
        maxColorIDX = 5
        cls.color = cls.colorList[cls.colorIDX]
        cls.colorIDX +=1
        if cls.colorIDX == maxColorIDX: cls.colorIDX = 0
        print("color: ", cls.color)
        return cls.color
        
    
    def dict2TrnNam(self, train):
        self.trnName = next(iter(train))
    def dict2ConNam(self, consist):
        self.conName = next(iter(consist))
        
    def newTrain(self):
        newTrain = {}
        newTrainNum = trainDB.numTrains+1
        newTrainNam = "train"+str(newTrainNum)
        newConsistNum = trainDB.numConsists+1 
        newConsistNam = "consist"+str(newConsistNum)
        tmpTrain = self.files.readFile("trainFile")
        
        newTrain[newTrainNam] = tmpTrain.pop("trnProtype")
        newTrain[newTrainNam]["trainNum"] = newTrainNum
        newTrain[newTrainNam]["consistNum"] = newConsistNum
        newTrain[newTrainNam]["trnObjTag"] = newTrainNam+"ObjTag"
    
        print("newTrain: dict: ", newTrain)
        trainDB.trains.update(newTrain)
        
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
        disp = dispObj()

        match trainDict["status"]:
            case "enroute":
                variance = np.random.normal(loc=0, scale=0.25, size=1)
                trainDict["timeEnRoute_Old"] = trainDict["timeEnRoute"]
                routeNam = trainDict["currentLoc"]
                routeStem = mVars.routes[routeNam]
                trainDict["deltaT"] = mVars.prms["timeStep"] + variance
                
                trainDict["timeEnRoute"] = trainDict["timeEnRoute_Old"] + trainDict["deltaT"]
                transTime = mVars.routes[trainDict["currentLoc"]]["transTime"]
                if mVars.prms["dbgTrnProc"]: print("trainCalcs: train: ", 
                    trainDict["trainNum"], "route: ", routeNam, 
                    ", origin: ", trainDict["origLoc"], ", dest:", trainDict["finalLoc"], 
                    ", direction: ", trainDict["direction"], ", transTime:", transTime, 
                    ", timeEnRoute: ", trainDict["timeEnRoute"], 
                    ", variance: ", variance)
                disp.drawTrain(trnName)
                if trainDict["timeEnRoute"] >= transTime:
                    #remove train from that route
                    try:
                        index = routeStem["trains"].index(trnName)
                    except:
                        pass
                    routeStem["trains"].pop(index)
                    gui.C.delete(routeStem["trnLabelTag"])
        
                    trainDict["currentLoc"] = trainDict["finalLoc"]
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
                disp.drawTrain(trnName)
                pass
            

