import numpy as np
import tkinter as tk
from mainVars import mVars
from fileProc import readFiles
from display import dispItems
from locProc import locProc
from stateVars import locs, trainDB, routeCls
np.set_printoptions(precision=2, suppress=True) 


#=================================================
class trainParams():
    trnHeight = 10
    trnLength = 20
    colorIDX = 0
    colorList = ["red", "green", "yellow", "orange", "purple1", "dodger blue", "deep pink",
                 "lawn green", "goldenrod", "OrangeRed2", "magenta2", "RoyalBlue1"]
    trnStatusList = ["enroute", "ready2Leave", "building", "built", "terminate", "switch",
                     "dropPickup", "continue", "turn", "misc", "stop"]


    def __init__(self):
        #self.trainID = int
        self.trnName = ""
        self.conName = ""
        self.files = readFiles()

        pass
    
    @classmethod
    def colors(cls):
        maxColorIDX = 12
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
        newTrain[newTrainNam]["trnRectTag"] = newTrainNam+"RectTag"
        newTrain[newTrainNam]["trnNumTag"] = newTrainNam+"NumTag"
        newTrain[newTrainNam]["trnLabelTag"] = newTrainNam+"LabelTag"
        newTrain[newTrainNam]["startTime"] = mVars.time
    
        print("newTrain: partial dict: ", newTrain)
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
        self.trnActionList = [""]

    def trainCalcs(self, trainDict, trnName):
        disp = dispItems()

        match trainDict["status"]:
            case "enroute":
                variance = np.random.normal(loc=0, scale=0.25, size=1)
                routeNam = trainDict["currentLoc"]
                routeStem = routeCls.routes[routeNam]
                trainDict["deltaT"] = mVars.prms["timeStep"] + variance
                trainDict["deltaT"] = round(trainDict["deltaT"].item(), 2)
                
                trainDict["timeEnRoute"] += trainDict["deltaT"]
                trainDict["timeEnRoute"] = round(trainDict["timeEnRoute"], 2)
                transTime = routeCls.routes[trainDict["currentLoc"]]["transTime"]
                if mVars.prms["dbgTrnProc"]: self.printTrnEnRoute(trainDict, routeNam, transTime, variance)
                
                disp.drawTrain(trnName)
                match trainDict["direction"]:
                    case "east":
                        if trainDict["xLoc"] >= routeCls.routes[routeNam]["x1"]:
                            self.procTrnStop(trainDict, trnName)
                    case "west":
                        if trainDict["xLoc"] <= routeCls.routes[routeNam]["x0"]:
                            self.procTrnStop(trainDict, trnName)
                                                
                    
            case "ready2Leave":
                #fills nextLoc with the route it is taking out of currentLoc
                #self.fillNextLoc(trainDict["currentLoc"], trainDict) 
                print("train: ", trnName, " switching to enroute status")
                trainDict["status"] = "enroute"
                disp.drawTrain(trnName)
                pass
            case "building"|"built":
                #procssing done in locProc
                pass
        # the following are status states for a train
        # they are also actions that a train can undergo in a 
        # location/terminal/destination
            case "terminate" | "continue":
                #procssing done in locProc
                pass
            case "switch" | "dropPickup":
                #procssing done in locProc
                pass
            case "stop":
                pass
         
    def printTrnEnRoute(self, trainDict, routeNam, transTime, variance):
        if mVars.prms["dbgTrnProc"]: print("trainCalcs: train: ", 
        trainDict["trainNum"], "route: ", routeNam, 
        ", origin: ", trainDict["origLoc"], ", dest:", trainDict["finalLoc"], 
        ", direction: ", trainDict["direction"], ", transTime:", transTime, 
        ", timeEnRoute: ", trainDict["timeEnRoute"], 
        ", variance: ", variance)

            
    def procTrnStop(self, trainDict, trnName):
        disp = dispItems()
        routeNam = trainDict["currentLoc"]
        routeStem = routeCls.routes[routeNam]
        consistNum = trainDict["consistNum"]
        consistNam = "consist"+str(consistNum)

        stopLoc = trainDict["nextLoc"]
        trainDict["currentLoc"] = stopLoc
        print("train: ", trnName, "entering terminal: ", stopLoc, "trainDict: ", trainDict)
        print("train: ", trnName, "consistNum: ", consistNum, 
              "contents: ", trainDB.consists[consistNam])
        
        #actions are executed in terminals/yards/switch areas
        #locProc takes care of these processes
        match trainDict["stops"][stopLoc]["action"]:
            case "terminate":
                trainDict["status"] = "terminate"
                trainDict["timeEnRoute"] = 0
                pass
            case "switch": 
                # switch town with road train
                trainDict["status"] = "switch"
                self.updateTrain4Stop(stopLoc, trainDict)

                # turn has the same processing as switch,
                # except train returns to origin after switching location
                pass
            case "dropPickup":
                # no industry switching done, just car exchange
                # switching typically done by yard crew at yards,
                # train crew at other locations
                trainDict["status"] = "dropPickup"
                trainDict["timeEnRoute"] = 0
                self.updateTrain4Stop(stopLoc, trainDict)
                pass
            case "continue":
                #no action at this stop - continue to nextLoc
                trainDict["status"] = "continue"
                trainDict["timeEnRoute"] = 0
                self.updateTrain4Stop(stopLoc, trainDict)

        disp.drawTrain(trnName)
        locs.locDat[trainDict["currentLoc"]]["trains"].append(trnName)
        try:
            index = routeStem["trains"].index(trnName)
        except:
            pass
        
        #remove train from that route
        routeStem["trains"].pop(index)
        #gui.C.delete(routeStem["trnLabelTag"])
        mVars.numOpBusy -=1

    def updateTrain4Stop(self, stopLoc, trainDict):
        trainDict["numStops"] -=1
        if trainDict["numStops"] == 0: 
            trainDict["status"] = "terminate"
            return
        self.fillNextLoc(stopLoc, trainDict)
        pass
    

    def fillNextLoc(self, stopLoc, trainDict):        
        print("getNextLoc: trainDict: ", trainDict)
        
        iterStops = iter(trainDict["stops"].keys())
        nextLoc = None
        for stop in iterStops:
            if stop == stopLoc:
                nextLoc = next(iterStops, None)
        if nextLoc == None: 
            print("no more locations")
            trainDict["status"] = "stop"
        else:
            trainDict["nextLoc"] = nextLoc
         
        print("getNextLoc: trainDict: ", trainDict)
            
        return 

