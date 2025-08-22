import random
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from display import dispItems
from dispatch import schedProc, dspCh
from yardCalcs import ydCalcs
from swCalcs import swCalcs
from stagCalcs import stCalcs
from gui import gui
from coords import transForms
from routeCalcs import routeCalcs, rtCaps
from outputMethods import printMethods
from locBase import locBase
        

np.set_printoptions(precision=2, suppress=True) 


dbgLocal = 1     
    
#=================================================
class locProc():
    
    def __init__(self):
        pass
    
    #classmethod:
    
    def printydTrains(self):
        if mVars.prms["dbgYdProc"]: print("trains analyzed: trainDB.ydTrains: ",
                    trainDB.ydTrains)
        
    def locCalcs(self, locStem, loc):
        locBaseObj = locBase()
        schedProcObj = schedProc()
        ydCalcObj = ydCalcs()
        swAreaObj = swCalcs()
        stagCalcObj = stCalcs()
        rtCapsObj = rtCaps()
        printObj = printMethods()

        if mVars.prms["dbgYdProc"]: 
            print("\nentering locCalcs: location: ", loc, ", locDat: ", locs.locDat[loc])

        locBaseObj.countCars(loc)
        rtCapsObj.updateRtSlots()
        #print("rtCaps.rtCap: ", rtCaps.rtCap)
        printObj.printRtCaps()
        schedProcObj.fetchLocSchedItem(loc)
        match locStem[loc]["type"]:
            case "yard":
                self.analyzeTrains(loc)
                self.printydTrains()
                ydCalcObj.yardMaster(loc)
            case "swArea":
                swAreaObj.swAnalyzeTrains(loc)
                self.printydTrains()
                swAreaObj.switchCalcs(loc)
            case "staging":
                stagCalcObj.stAnalyzeTrains(loc)
                self.printydTrains()
                stagCalcObj.staging(loc)

                    
        #dispObj.dispTrnLocDat(loc)
            
    def analyzeTrains(self, loc):
        trainDB.ydTrains = {"brkDnTrn": [], "buildTrain": [], "swTrain": [], "rdCrwSw": [], "continue": []}
        rtCapsObj = rtCaps()

        # train status leads to actions by the yard crew or
        # the train crew.  Train actions are the same name as
        # the corresponding train status string
        for trainNam in locs.locDat[loc]["trains"]:
            match trainDB.trains[trainNam]["status"]:
                case "terminate":
                    if trainNam not in trainDB.ydTrains["brkDnTrn"]:
                        trainDB.ydTrains["brkDnTrn"].append(trainNam)
                case "dropPickup":
                    # in a yard this action is often undertaken by 
                    # the yard crew; hence a yard action
                    if trainNam not in trainDB.ydTrains["swTrain"]:
                        trainDB.ydTrains["swTrain"].append(trainNam)
                case "building"|"init":
                    # for yards, not switch areas
                    if trainNam not in trainDB.ydTrains["buildTrain"]:
                        trainDB.ydTrains["buildTrain"].append(trainNam)
                case "rdCrwSw":
                    # for switch areas no yards
                    # code is in locProc but actions are undertaken by
                    # the virtual train crew
                    if trainNam not in trainDB.ydTrains["rdCrwSw"]:
                        trainDB.ydTrains["rdCrwSw"].append(trainNam)
                    pass
                case "continue":
                    # no action for yard.  May have a call to 
                    # dispatcher eventually, so process "continue" here 
                    # as no action needed by train crew (modulo dispatch call)
                    locs.locDat[loc]["trnCnts"]["passThru"] += 1
                    self.startTrain(loc, trainNam)
                case "built":
                    startTime = trainDB.trains[trainNam]["startTime"]
                    if (mVars.time >= startTime):
                        locs.locDat[loc]["trnCnts"]["started"] += 1
                        #locs.locDat[loc]["bldTrnDepTimes"].pop(0)
                        nextLoc = trainDB.trains[trainNam]["nextLoc"]
                        #dispItemsObj.clearTrnRecs(trainNam)
                        print(trainNam, ": with start time ", startTime,
                              " in loc: ", loc, 
                              " built and leaving for (nextLoc): ", 
                              nextLoc)
                        self.startTrain(loc, trainNam)
        

    def startTrain(self, loc, trainNam):
        # setup train
        dispObj = dispItems()
        coordObj = transForms()
        locBaseObj = locBase()
        rtCapsObj = rtCaps()
        
        trainStem = trainDB.trains[trainNam]
        trainStem["status"] = "wait4Clrnce"
        if trainStem["rtToEnter"] == "":
            locBaseObj.findRtPrms(loc, trainNam)
        routeNam = trainStem["rtToEnter"]
        #trainStem["currentLoc"] = routeNam
               
        #sets initial coords in rotated system 
        if (trainStem["coord"]["xTrnInit"] == 0) or\
            (trainStem["coord"]["xTrnInit"]) == None:
            #train not on route to start
            trainStem["coord"]["xTrnInit"] = 0  
        locBaseObj.addTrn2LocOrRt(routeNam, trainStem, trainNam)
        #rtCapsObj.addTrn2RouteQ(routeNam, trainNam)
        trainStem["firstDispTrn"] = 1
        
        #print("trainStem: ", trainStem, ", original dict: ", trainDB.trains[trainNam])
        dispObj.drawTrain(trainNam)
                
        if mVars.prms["dbgYdProc"]: print("train",trainNam," starting: "
            ,trainStem, ",\n")
            #route: ", routeCls.routes[route4newTrn])

    def printCoords(self):
        """
        eastXPlot = gui.guiDict[loc]["x1"]
        westXPlot = gui.guiDict[loc]["x0"] - trainInit.trnLength
        eastYPlot = gui.guiDict[leftObj]["y0"] - gui.guiDict["locDims"]["height"]*0.25
        if trainStem["direction"] == "west": 
            trainStem["coord"]["xPlot"] -= trainInit.trnLength
            westXPlotTransform = trainStem["coord"]["xPlot"]
            print("westXPlot no transform: ", westXPlot, ", with transform: ", 
                westXPlotTransform)
        else:
            print("test of coord transform: \neastXPlot no transform: ", 
                eastXPlot, ", with transform: ", 
                trainStem["coord"]["xPlot"])
            print("eastYPlot no transform: ", eastYPlot, ", with transform: ", 
                trainStem["coord"]["yPlot"])
        """
        pass

