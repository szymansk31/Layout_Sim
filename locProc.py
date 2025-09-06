import random
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from display import dispItems
from dispatch import schedProc, dspCh
from gui import gui
from routeProc import routeMgmt, rtCaps
from locBase import locBase, Qmgmt, locMgmt
        

np.set_printoptions(precision=2, suppress=True) 


dbgLocal = 1     
    
#=================================================
class locProc():
    
    def __init__(self):
        self.locQmgmtObj = Qmgmt()
        self.locBaseObj = locBase()
        self.locMgmtObj = locMgmt()
        self.schedProcObj = schedProc()
        self.dispObj = dispItems()
        self.rtCapsObj = rtCaps()
      
    #classmethod:
    
    def printydTrains(self):
        if mVars.prms["dbgYdProc"]: print("trains analyzed: trainDB.ydTrains: ",
                    trainDB.ydTrains)
        
    def locCalcs(self, loc):
        from yardCalcs import ydCalcs
        from swCalcs import swCalcs
        from stagCalcs import stCalcs
        self.ydCalcObj = ydCalcs()
        self.swAreaObj = swCalcs()
        self.stagCalcObj = stCalcs()

        if mVars.prms["dbgYdProc"]: 
            print("\nentering locCalcs: location: ", loc, ", locDat: ", locs.locDat[loc])

        locStem = locs.locDat[loc]
        self.locBaseObj.countCars(loc)
        self.schedProcObj.fetchLocSchedItem(loc)
        match locStem["type"]:
            case "yard":
                self.analyzeTrains(loc)
                self.printydTrains()
                self.ydCalcObj.yardMaster(loc)
            case "swArea":
                self.swAreaObj.swAnalyzeTrains(loc)
                self.printydTrains()
                self.swAreaObj.switchCalcs(loc)
            case "staging":
                self.stagCalcObj.stAnalyzeTrains(loc)
                self.printydTrains()
                self.stagCalcObj.staging(loc)

                    
        #dispObj.dispTrnLocDat(loc)
            
    def analyzeTrains(self, loc):
        trainDB.ydTrains = {"brkDnTrn": [], "buildTrain": [], "swTrain": [], "rdCrwSw": [], "continue": []}

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


    def procWorkingQ(self, loc):
        locStem = locs.locDat[loc]
        self.locQmgmtObj.sortLocQ("working", "estDeptTime")
        for QDict in locStem["Qs"]["working"]:
            trainNam = next(iter(QDict))
            estDeptTime = trainDB.trains[trainNam]["estDeptTime"]
            locArrTime = trainDB.trains[trainNam]["locArrTime"]
            if (mVars.time >= estDeptTime) or \
                ((mVars.time - locArrTime) >= mVars.prms["mxTrnDwlTim"]):
                nextLoc = trainDB.trains[trainNam]["nextLoc"]
                #dispItemsObj.clearTrnRecs(trainNam)
                print(trainNam, ": with departure time ", estDeptTime,
                        " in loc: ", loc, 
                        "leaving for (nextLoc): ", 
                        nextLoc)
                self.startTrain(loc, trainNam)


    def startTrain(self, loc, trainNam):
        # setup train
        
        trainStem = trainDB.trains[trainNam]
        trainStem["status"] = "wait4Clrnce"
        if trainStem["rtToEnter"] == "":
            self.locMgmtObj.findRtPrms(loc, trainNam)
        routeNam = trainStem["rtToEnter"]
        trainStem["estArrTime"] = mVars.time + routeCls.routes[routeNam]["transTime"]
        self.locMgmtObj.placeTrain(routeNam, trainStem, trainNam)
        self.locQmgmtObj.remTrnLocQ(loc, "working", trainNam)
        #self.rtCapsObj.addTrn2RouteQ(routeNam, trainNam)
        trainStem["firstDispTrn"] = 1
        
        #print("trainStem: ", trainStem, ", original dict: ", trainDB.trains[trainNam])
        self.dispObj.drawTrain(trainNam)
        locs.locDat[loc]["trnCnts"]["started"] += 1
                
        if mVars.prms["dbgYdProc"]: print("train",trainNam," starting: "
            ,trainStem, ",\n")
            #route: ", routeCls.routes[route4newTrn])

    def printCoords(self):
        """
        eastXPlot = gui.guiDict[loc]["x1"]
        westXPlot = gui.guiDict[loc]["x0"] - trainInit.trnLength
        eastYPlot = gui.guiDict[westObj]["y0"] - gui.guiDict["locDims"]["height"]*0.25
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

