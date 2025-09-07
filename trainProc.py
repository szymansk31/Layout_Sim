import numpy as np
import tkinter as tk
from mainVars import mVars
from fileProc import readFiles
from stateVars import locs, dspCh, trainDB, routeCls
np.set_printoptions(precision=2, suppress=True) 
  
class trnProc:    
    
    def __init__(self):
        from locBase import locBase, Qmgmt, locMgmt
        self.locBaseObj = locBase()
        self.locQmgmtObj = Qmgmt()
        self.locMgmtObj = locMgmt()
        from routeProc import routeMgmt, rtCaps
        self.rtMgmtObj = routeMgmt()
        self.rtCapsObj = rtCaps()
        from display import dispItems
        self.dispObj = dispItems()
        from coords import transForms
        self.coordObj = transForms()
        from dispatch import clearTrnCalcs
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
                distTot = round(trainDict["timeEnRoute"]*velocity, 2)
                print("distance via timeEnRoute: ", distTot)
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
                                                
            case "waitOnRoute":
                pass
            case "wait4Clrnce" if mVars.prms["useDispatch"] == False:
                print("train: ", trainNam, " switching to enroute status")
                trainDict["status"] = "enroute"
                trainDict["currentLoc"] = trainDict["rtToEnter"]
                self.rtMgmtObj.addTrn2Route(trainDict["currentLoc"], trainNam)
                # remove train rectangles above the location rectangle
                self.dispObj.drawTrain(trainNam)
                loc = trainDB.trains[trainNam]["departStop"]
                if loc != "":
                    arrTrk = self.locQmgmtObj.readArrTrk(loc, trainNam)
                    #remove train from location arrivals Queue
                    self.locQmgmtObj.remTrnLocQ(loc, trainNam)
                    #remove train from loc["trkPrms"]["arrTrk"]
                    self.locQmgmtObj.remTrnArrTrk(loc, arrTrk, trainNam)
                    #remove train from loc["trains"] list
                    self.locMgmtObj.rmTrnFrmLoc(loc, trainNam)
                    #remove train rectangle from action list above loc
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
            self.rtMgmtObj.remTrnsOnRoute(routeNam, trainNam)
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
                #self.dispObj.clearRouteTrnRecs(trainNam)
                pass
            case "rdCrwSw": 
                from swCalcs import swCalcs
                # switch town with road train
                trainDict["status"] = "rdCrwSw"
                # setup list of industries when first entering swArea
                swCalcs.indusIter = iter(locs.locDat[stopLoc]["industries"])
                trainDict["estDeptTime"] = mVars.time + trainDB.avgSwTime
                self.updateTrain4Stop(stopLoc, trainDict, trainNam, arrTrk)
                pass
            case "dropPickup":
                # no industry switching done, just car exchange
                # switching typically done by yard crew at yards,
                # train crew at other locations
                trainDict["status"] = "dropPickup"
                trainDict["estDeptTime"] = mVars.time + trainDB.avgSwTime
                self.updateTrain4Stop(stopLoc, trainDict, trainNam, arrTrk)
            case "continue":
                #no action at this stop - continue to nextLoc
                trainDict["status"] = "continue"
                trainDict["estDeptTime"] = mVars.time + trainDB.avgContTime
                self.updateTrain4Stop(stopLoc, trainDict, trainNam, arrTrk)

        self.locMgmtObj.findRtPrms(stopLoc, trainNam)
        self.dispObj.drawTrain(trainNam)
        self.locMgmtObj.placeTrain(stopLoc, trainDict, trainNam)

        #routeStem["trains"].pop(index)
        mVars.numOpBusy -=1

    def updateTrain4Stop(self, stopLoc, trainDict, trainNam, arrTrk):
        trainDict["numStops"] -=1
        if trainDict["numStops"] == 0: 
            trainDict["status"] = "terminate"
            return
        self.fillNextLoc(stopLoc, trainDict)

        trainDict["timeEnRoute"] = 0
       
    

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

