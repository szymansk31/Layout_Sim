import numpy as np
import tkinter as tk
from mainVars import mVars
from fileProc import readFiles
from display import dispItems
from locBase import locBase
from coords import transForms
from stateVars import locs, dspCh, trainDB, routeCls
from routeCalcs import rtCaps
np.set_printoptions(precision=2, suppress=True) 
  
class trnProc:    
    
    def __init__(self):
        self.locBaseObj = locBase()
        pass
    
    def trainCalcs(self, trainDict, trainNam):
        dispObj = dispItems()
        coordObj = transForms()
        rtCapsObj = rtCaps()

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
                dispObj.drawTrain(trainNam)
                match trainDict["direction"]:
                    case "east":
                        if trainDict["coord"]["xPlot"] >= routeCls.routes[routeNam]["x1"]:
                            self.procTrnStop(trainDict, trainNam)
                    case "west":
                        if trainDict["coord"]["xPlot"] <= routeCls.routes[routeNam]["x0"]:
                            self.procTrnStop(trainDict, trainNam)
                                                
                    
            case "wait4Clrnce" if rtCapsObj.checkRtSlots(trainNam):
                print("train: ", trainNam, " switching to enroute status")
                trainDict["status"] = "enroute"
                trainDict["currentLoc"] = trainDict["rtToEnter"]
                self.locBaseObj.fillTrnsOnRoute(trainDict["currentLoc"], trainNam)
                # remove train rectangles above the location rectangle
                dispObj.drawTrain(trainNam)
                loc = trainDB.trains[trainNam]["departStop"]
                if loc != "":
                    self.locBaseObj.rmTrnFrmLoc(loc, trainNam)
                    dispObj.clearActionTrnRecs(loc, trainNam)
                pass
            case "wait4Clrnce" if not rtCapsObj.checkRtSlots(trainNam):
                rtCapsObj.addTrn2RouteQ(trainDict["rtToEnter"], trainNam)
                
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
        dispObj = dispItems()
        rtCapsObj = rtCaps()
        routeNam = trainDict["currentLoc"]
        consistNum = trainDict["consistNum"]
        consistNam = "consist"+str(consistNum)

        stopLoc = trainDict["nextLoc"]
        trainDict["locArrTime"] = mVars.time
        trainDict["rtToEnter"] = ""
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
                dispObj.clearRouteTrnRecs(trainNam)
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

        dispObj.drawTrain(trainNam)
        self.locBaseObj.addTrn2LocOrRt(stopLoc, trainDict, trainNam)

        #remove train from that route
        self.locBaseObj.remTrnsOnRoute(routeNam, trainNam)
        #routeStem["trains"].pop(index)
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

