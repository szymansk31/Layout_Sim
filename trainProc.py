import numpy as np
import tkinter as tk
from mainVars import mVars
from fileProc import readFiles
from display import dispItems
from locProc import locProc, locBase
from coords import transForms
from stateVars import locs, dspCh, trainDB, routeCls
np.set_printoptions(precision=2, suppress=True) 


#=================================================
class trainInit():
    trnHeight = 10
    trnLength = 20
    colorIDX = 0
    colorList = ["red", "green", "yellow", "orange", "purple1", "dodger blue", "deep pink",
                 "lawn green", "goldenrod", "OrangeRed2", "magenta2", "RoyalBlue1"]
    trnStatusList = ["enroute", "ready2Leave", "init", "building", "built", "terminate", "rdCrwSw",
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
    def addTrn2TrainDB(trainDict):
        trainDB.trains.update(trainDict)

    def numCars(self, train):
        consistNam = trainDB.getConNam(train)
        consist = trainDB.consists[consistNam]
        numCars = 0
        for loc in consist["stops"]:
            numCars += sum(consist["stops"][loc].values())
        return numCars
            
    def newTrain(self, newTrainNam):
        newTrain = {}
        #newTrainNum = trainDB.numTrains+1
        newTrainNum = newTrainNam[5:]
        #newTrainNam = "train"+str(newTrainNum)
        newConsistNum = trainDB.numConsists+1 
        newConsistNam = "consist"+str(newConsistNum)
        tmpTrain = self.files.readFile("trainFile")
        
        newTrain[newTrainNam] = tmpTrain.pop("trnProtype")
        newTrain[newTrainNam]["trainNum"] = newTrainNum
        newTrain[newTrainNam]["consistNum"] = newConsistNum
        newTrain[newTrainNam]["numCars"] = 0
        newTrain[newTrainNam]["trnRectTag"] = newTrainNam+"RectTag"
        newTrain[newTrainNam]["trnNumTag"] = newTrainNam+"NumTag"
        newTrain[newTrainNam]["trnLabelTag"] = newTrainNam+"LabelTag"
        #newTrain[newTrainNam]["startTime"] = mVars.time
    
        print("newTrain: partial dict: ", newTrain)
        trainDB.trains.update(newTrain)
        
        self.newConsist(newConsistNum, newTrainNum)
        trainDB.numTrains +=1
        trainDB.numConsists +=1
        return newConsistNam
    
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

    def initNewTrain(self, loc, newTrainNam):
        conName = self.newTrain(newTrainNam)
        
        #nextLoc, numstops, stops = self.setStops(loc, maxCarTrk)
        stops = trainDB.trains[newTrainNam]["stops"]
        numStops = 0
        for stopLoc in stops:
            numStops += 1 
        nextLoc = next(iter(stops))
        print("train: ", newTrainNam, ", stops: ", stops)
        trainDB.trains[newTrainNam].update( {
            "status": "building",
            "origLoc": loc,
            "nextLoc": nextLoc,
            "currentLoc": loc,
            "finalLoc": stopLoc,
            "numStops": numStops,
            "departStop": loc,
            "stops": stops,
            "color": trainInit.colors()           
                })
        # consist gets stops that have cars to drop, not those where
        # the train continues through.  Pickups are triggered by
        # "dropPickup" status in that location and will add to consists
        for conStop in stops:
            tmpDict = {conStop: {"box": 0, "tank": 0,"rfr": 0, "hop": 0, 
            "gons": 0, "flats": 0}}
        trainDB.consists[conName].update({
            "stops": tmpDict
        })
        
        print("new train: ", newTrainNam, ": ", trainDB.trains[newTrainNam])
        print("new consist: ", conName, ":", trainDB.consists[conName])
        trainDB.ydTrains["buildTrain"].append(newTrainNam)
        return

    

  
class trnProc:    
    
    def __init__(self):
        self.timeEnRoute_Old = 0
        self.trainImage = any
        self.deltaT = 0.0
        self.trnActionList = [""]

    def trainCalcs(self, trainDict, trainNam):
        disp = dispItems()
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
                #    locBaseObj.rmTrnFrmLoc(loc, trainNam)
                pass
            case "building"|"built"|"init":
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
        locBaseObj = locBase()
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
        locBase.addTrn2Loc(stopLoc, trainNam)
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

