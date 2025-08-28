import numpy as np
import tkinter as tk
from mainVars import mVars
from fileProc import readFiles
from display import dispItems
from locBase import locBase, Qmgmt, locMgmt
from coords import transForms
from stateVars import locs, dspCh, trainDB, routeCls
from routeCalcs import routeMgmt, rtCaps
from dispatch import clearTrnCalcs
np.set_printoptions(precision=2, suppress=True) 
  
class trnProc:    
    
    def __init__(self):
        self.locBaseObj = locBase()
        self.locQmgmtObj = Qmgmt()
        self.locMgmtObj = locMgmt()
        self.rtMgmtObj = routeMgmt()
        self.rtCapsObj = rtCaps()
        self.dispObj = dispItems()
        self.coordObj = transForms()
        self.clrTrnObj = clearTrnCalcs()
        pass
    
    def trainCalcs(self, trainDict, trainNam):

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
                
                self.coordObj.xRoute2xPlot(routeNam, trainNam)
                self.dispObj.drawTrain(trainNam)
                match trainDict["direction"]:
                    case "east":
                        if trainDict["coord"]["xPlot"] >= routeCls.routes[routeNam]["x1"]:
                            self.procTrnStop(trainDict, trainNam)
                    case "west":
                        if trainDict["coord"]["xPlot"] <= routeCls.routes[routeNam]["x0"]:
                            self.procTrnStop(trainDict, trainNam)
                                                
                    
            case "wait4Clrnce" if self.clrTrnObj.clearTrn(trainDict["nextLoc"], trainNam):
                print("train: ", trainNam, " switching to enroute status")
                trainDict["status"] = "enroute"
                trainDict["currentLoc"] = trainDict["rtToEnter"]
                self.rtMgmtObj.fillTrnsOnRoute(trainDict["currentLoc"], trainNam)
                # remove train rectangles above the location rectangle
                self.dispObj.drawTrain(trainNam)
                loc = trainDB.trains[trainNam]["departStop"]
                if loc != "":
                    self.locMgmtObj.rmTrnFrmLoc(loc, trainNam)
                    self.dispObj.clearActionTrnRecs(loc, trainNam)
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
        routeNam = trainDict["currentLoc"]
        consistNum = trainDict["consistNum"]
        consistNam = "consist"+str(consistNum)

        stopLoc = trainDict["nextLoc"]
        trainDict["locArrTime"] = mVars.time
        trainDict["rtToEnter"] = ""
        trainDict["currentLoc"] = stopLoc
        trainDict["departStop"] = stopLoc
        QStem = locs.locDat[stopLoc]["Qs"]["arrivals"]
        if mVars.prms["useDispatch"] == True:
            idx = [idx for idx, QDict in enumerate(QStem) if trainNam in QDict]
            arrTrk = QStem[idx[0]][trainNam]["arrTrk"]
            self.locQmgmtObj.remTrnLocQ(stopLoc, "arrivals", trainNam)
        trainDict["coord"]["xTrnInit"] = 0 # reset for next route
        print("train: ", trainNam, "entering terminal: ", stopLoc, "trainDict: ", trainDict)
        print("train: ", trainNam, "consistNum: ", consistNum, 
              "contents: ", trainDB.consists[consistNam])
        
        #actions are executed in terminals/yards/switch areas
        #locProc takes care of these processes
        match trainDict["stops"][stopLoc]["action"]:
            case "terminate":
                trainDict["status"] = "terminate"
                trainDict["timeEnRoute"] = 0
                trainDict["estDeptTime"] = mVars.time + trainDB.avgSwTime
                self.dispObj.clearRouteTrnRecs(trainNam)
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
                self.updateTrain4Stop(stopLoc, trainDict)
                pass
            case "continue":
                #no action at this stop - continue to nextLoc
                trainDict["status"] = "continue"
                self.updateTrain4Stop(stopLoc, trainDict)

        self.locQmgmtObj.addTrn2LocQ(stopLoc, "departs", trainNam, arrTrk)
        self.dispObj.drawTrain(trainNam)
        self.locMgmtObj.placeTrain(stopLoc, trainDict, trainNam)

        #remove train from that route
        self.rtMgmtObj.remTrnsOnRoute(routeNam, trainNam)
        #routeStem["trains"].pop(index)
        mVars.numOpBusy -=1

    def updateTrain4Stop(self, stopLoc, trainDict):
        trainDict["numStops"] -=1
        if trainDict["numStops"] == 0: 
            trainDict["status"] = "terminate"
            return
        self.fillNextLoc(stopLoc, trainDict)
        trainDict["timeEnRoute"] = 0
        trainDict["estDeptTime"] = mVars.time + trainDB.avgContTime
        pass
    

    def fillNextLoc(self, stopLoc, trainDict):        
        print("fillNextLoc: trainDict: ", trainDict)
        
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
         
        print("fillNextLoc: trainDict: ", trainDict)
            
        return 

