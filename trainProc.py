import numpy as np
import tkinter as tk
from mainVars import mVars
from fileProc import readFiles
from display import dispItems
from locProc import locProc
from coords import transForms
from stateVars import locs, trainDB, routeCls
np.set_printoptions(precision=2, suppress=True) 


#=================================================
class trainParams():
    trnHeight = 10
    trnLength = 20
    colorIDX = 0
    colorList = ["red", "green", "yellow", "orange", "purple1", "dodger blue", "deep pink",
                 "lawn green", "goldenrod", "OrangeRed2", "magenta2", "RoyalBlue1"]
    trnStatusList = ["enroute", "ready2Leave", "building", "built", "terminate", "rdCrwSw",
                     "dropPickup", "continue", "turn", "misc", "stop"]


    def __init__(self):
        #self.trainID = int
        self.trainNam = ""
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
        self.trainNam = next(iter(train))
    def dict2ConNam(self, consist):
        self.conName = next(iter(consist))

    def numCars(self, train):
        consistNam = trainDB.getConNam(train)
        consist = trainDB.consists[consistNam]
        numCars = 0
        for loc in consist["stops"]:
            numCars += sum(consist["stops"][loc].values())
        return numCars
            
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
                    "gons": 0, "flats": 0},
                }
            }
        })
        return 


  
class trnProc:    
    
    def __init__(self):
        self.timeEnRoute_Old = 0
        self.trainImage = any
        self.deltaT = 0.0
        self.trnActionList = [""]

    def trainCalcs(self, trainDict, trainNam):
        disp = dispItems()
        locProcObj = locProc()
        coordObj = transForms()

        match trainDict["status"]:
            case "enroute":
                variance = np.random.normal(loc=0, scale=0.25, size=1)
                routeNam = trainDict["currentLoc"]
                routeStem = routeCls.routes[routeNam]
                deltaT = mVars.prms["timeStep"] + variance
                deltaT = round(deltaT.item(), 2)
                velocity = routeStem["distPerTime"]

                # Note that deltaX is in the rotated coord system.
                deltaX = int(deltaT*velocity)
                if trainDict["direction"] == "west": deltaX = -deltaX
                trainDict["deltaX"] = deltaX
                trainDict["coord"]["xRoute"] += deltaX
                trainDict["timeEnRoute"] += deltaT
                trainDict["timeEnRoute"] = round(trainDict["timeEnRoute"], 2)
                print("distance via timeEnRoute: ", trainDict["timeEnRoute"]*velocity)
                transTime = routeCls.routes[trainDict["currentLoc"]]["transTime"]
                if mVars.prms["dbgTrnProc"]: self.printTrnEnRoute(trainDict, routeNam, transTime, variance, deltaX)
                
                coordObj.xRoute2xPlot(routeNam, trainNam)
                disp.drawTrain(trainNam)
                match trainDict["direction"]:
                    case "east":
                        if trainDict["coord"]["xPlot"] >= routeCls.routes[routeNam]["x1"]:
                            self.procTrnStop(trainDict, trainNam)
                    case "west":
                        if trainDict["coord"]["xPlot"] <= routeCls.routes[routeNam]["x0"]:
                            self.procTrnStop(trainDict, trainNam)
                                                
                    
            case "ready2Leave":
                print("train: ", trainNam, " switching to enroute status")
                trainDict["status"] = "enroute"
                disp.drawTrain(trainNam)
                #loc = trainDB.trains[trainNam]["departStop"]
                #if loc != "":
                #    locProcObj.rmTrnFrmLoc(loc, trainNam)
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
            case "rdCrwSw" | "dropPickup":
                #procssing done in locProc
                pass
            case "stop":
                pass
         
    def printTrnEnRoute(self, trainDict, routeNam, transTime, variance, deltaX):
        if mVars.prms["dbgTrnProc"]: print("trainCalcs: train: ", 
        trainDict["trainNum"], "route: ", routeNam, 
        ", origin: ", trainDict["origLoc"], ", dest:", trainDict["finalLoc"], 
        ", direction: ", trainDict["direction"], ", transTime:", transTime, 
        ", timeEnRoute: ", trainDict["timeEnRoute"], 
        ", variance: ", variance, ", dist this step: ", deltaX)

            
    def procTrnStop(self, trainDict, trainNam):
        disp = dispItems()
        routeNam = trainDict["currentLoc"]
        routeStem = routeCls.routes[routeNam]
        consistNum = trainDict["consistNum"]
        consistNam = "consist"+str(consistNum)

        stopLoc = trainDict["nextLoc"]
        trainDict["currentLoc"] = stopLoc
        trainDict["departStop"] = stopLoc
        print("train: ", trainNam, "entering terminal: ", stopLoc, "trainDict: ", trainDict)
        print("train: ", trainNam, "consistNum: ", consistNum, 
              "contents: ", trainDB.consists[consistNam])
        
        #actions are executed in terminals/yards/switch areas
        #locProc takes care of these processes
        match trainDict["stops"][stopLoc]["action"]:
            case "terminate":
                trainDict["status"] = "terminate"
                trainDict["timeEnRoute"] = 0
                pass
            case "rdCrwSw": 
                from swCalcs import swCalcs
                # switch town with road train
                trainDict["status"] = "rdCrwSw"
                # setup list of industries when first entering swArea
                swCalcs.indusIter = iter(locs.locDat[stopLoc]["industries"])
                self.updateTrain4Stop(stopLoc, trainDict)
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

        disp.drawTrain(trainNam)
        locs.locDat[trainDict["currentLoc"]]["trains"].append(trainNam)
        try:
            index = routeStem["trains"].index(trainNam)
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

