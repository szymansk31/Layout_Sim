import random
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from display import dispItems
from dispatch import schedProc
from yardCalcs import ydCalcs
from swCalcs import swCalcs
from stagCalcs import stCalcs
from gui import gui
from coords import transForms
from dispatch import rtCaps
from outputMethods import printMethods
        

np.set_printoptions(precision=2, suppress=True) 


dbgLocal = 1     
#=================================================
class locBase():
    
    def __init__(self):
        pass
    
    def initLocDicts(self):
        from fileProc import readFiles
        files = readFiles()
        print("initializing location dicts: ")
        locs.locDat = files.readFile("locationFile")
        for loc in locs.locDat:
            self.countCars(loc)
            locs.locDat[loc]["locTrnRectID"] = loc+"TrnRectID"
            locs.locDat[loc]["locTrnNumID"] = loc+"TrnNumID"
            locs.locDat[loc]["locRectID"] = loc+"RectID"
        
    def countCars(self, loc):
        locStem = locs.locDat[loc]
        type = locs.locDat[loc]["type"]
        locStem["totCars"] = 0
        match type:
            case "yard":
                trackStem = locStem["tracks"]
            case "swArea":
                trackStem = locStem["industries"]
        for trackNam in locStem["destTrkTots"]:
            #print("\n Location: ", loc, "destination: ", trackNam)
            if trackNam not in trackStem: continue
            match type:
                case "yard":
                    locStem["destTrkTots"][trackNam] = sum(trackStem[trackNam].values())
                    locStem["totCars"] += locStem["destTrkTots"][trackNam]
                case "swArea":
                    if trackNam == "offspot": 
                        locStem["numOffspot"] = sum(locs.locDat[loc]["offspot"].values())
                        continue
                    locStem["indusTots"][trackNam] = \
                        sum(trackStem[trackNam]["pickups"].values()) + \
                        sum(trackStem[trackNam]["leave"].values())
                    locStem["totCars"] += locStem["indusTots"][trackNam]
                    locStem["totCars"] += locStem["numOffspot"]
                    
        #print("countCars: ", locStem)
                        

    def locDests(self, loc):
        thisLocDests = []
        for dest in locs.locDat[loc]["destTrkTots"]:
            thisLocDests.append(dest)
        return thisLocDests

    def rmTrnFrmActions(self, action, loc, ydTrainNam):
        dispObj = dispItems()
        # remove train from ydTrains and location
        print("rmTrnFrmActions: trainDB.ydTrains: ", trainDB.ydTrains)
        index = trainDB.ydTrains[action].index(ydTrainNam)
        trainDB.ydTrains[action].pop(index)
        if dbgLocal: print("after removal: trainDB.ydTrains: ", trainDB.ydTrains, 
                "\n trains[ydTrainNam]: ", trainDB.trains[ydTrainNam])
        # clear action data from display
        dispObj.clearActionDat(loc)
    
    def rmTrnFrmLoc(self, loc, trainNam):  
        index = locs.locDat[loc]["trains"].index(trainNam)
        locs.locDat[loc]["trains"].pop(index)

    def addTrn2Loc_rt(loc, trainStem, trainNam): 
        rtCapsObj = rtCaps()
        coordObj = transForms()
        currentLoc = trainStem["currentLoc"]
        if "route" in currentLoc:
            routeStem = routeCls.routes[currentLoc] 
            #routeCls.routes[trainStem["currentLoc"]]["trains"].append(trainNam)
            rtCapsObj.fillTrnsOnRoute(currentLoc, trainNam)
            # fill trainDB with xPlot and yPlot, the canvas/screen coords
            coordObj.xRoute2xPlot(loc, trainNam)
            return
        else:
            locs.locDat[loc]["trains"].append(trainNam)
            return

    def cleanupSwAction(self, loc, ydTrainNam, action):
        dispObj = dispItems()
        locActionStem = locs.locDat[loc]["trn4Action"]            
        index = [i for i, d in enumerate(locActionStem)\
            if action in d]
        if index:
            locActionStem.pop(index[0])
        try:
            trainStem = trainDB.trains[ydTrainNam]
            # remove stop from train
            trainStem["stops"].pop(loc)
            # remove stop from consist
            consistNam = trainDB.getConNam(ydTrainNam)
            trainDB.consists[consistNam]["stops"].pop(loc)
        except:
            pass
        # remove from ydTrains action list
        self.rmTrnFrmActions(action, loc, ydTrainNam)

        # clear action data from display
        dispObj.clearActionDat(loc)

    
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
                    if (mVars.time >= startTime) and rtCapsObj.checkRtSlots:
                        locs.locDat[loc]["trnCnts"]["started"] += 1
                        #locs.locDat[loc]["bldTrnDepTimes"].pop(0)
                        nextLoc = trainDB.trains[trainNam]["nextLoc"]
                        #dispItemsObj.clearTrnRecs(trainNam)
                        print(trainNam, ": with start time ", startTime,
                              " in loc: ", loc, 
                              " built and leaving for (nextLoc): ", 
                              nextLoc)
                        self.startTrain(loc, trainNam)
        
                
    def findRoutes(self, loc, ydTrainNam):
        nextLoc = trainDB.trains[ydTrainNam]["nextLoc"]
        for routeNam in routeCls.routes:
            loc = ''.join(loc)
            dest = ''.join(nextLoc)
            if dbgLocal: print("routNam: ", routeNam, " loc: ", loc, 
                " nextLoc: ", dest, "route: ", routeCls.routes[routeNam])
            if (loc in routeCls.routes[routeNam].values()) and \
                (dest in routeCls.routes[routeNam].values()):
                return routeNam

    def setRtTrnPrms(self, loc, ydTrainNam):
        # setup train
        trainStem = trainDB.trains[ydTrainNam]
        dest = trainDB.trains[ydTrainNam]["nextLoc"]
        if dest != "":
            # setup new route
            route4newTrn = self.findRoutes(loc, ydTrainNam)
            trainStem["rtToEnter"] = route4newTrn
            leftObj = routeCls.routes[route4newTrn]["leftObj"].strip()
            rtObj = routeCls.routes[route4newTrn]["rtObj"].strip()
            #routeCls.routes[route4newTrn]["trains"].append(ydTrainNam)
            if loc == leftObj: 
                trainStem["direction"] = "east"
            elif loc == rtObj:
                trainStem["direction"] = "west"
            else: 
                print("no route found", ydTrainNam,  "leftObj: ", leftObj, "rtObj: "
                        , rtObj,"loc: ", loc, "direction: ", trainStem["direction"])
                trainStem["status"] = "stop"
        return 
                    

    def startTrain(self, loc, ydTrainNam):
        # setup train
        dispObj = dispItems()
        coordObj = transForms()
        locBaseObj = locBase()
        rtCapsObj = rtCaps()
        
        trainStem = trainDB.trains[ydTrainNam]
        trainStem["status"] = "wait4Clearance"
        routeNam = trainStem["rtToEnter"]
                
        rtCapsObj.fillTrnsOnRoute(routeNam, ydTrainNam)
        trainStem["firstDispTrn"] = 1
        trainStem["currentLoc"] = routeNam
        
        #sets initial coords in rotated system    
        trainStem["coord"]["xTrnInit"] = 0  # train starting at location
        self.setTrnCoord(trainStem["currentLoc"], trainStem)  
        # xPlot and yPlot are in the screen coord system              
        coordObj.xRoute2xPlot(routeNam, ydTrainNam)
        #print("trainStem: ", trainStem, ", original dict: ", trainDB.trains[ydTrainNam])
        locBaseObj.rmTrnFrmLoc(loc, ydTrainNam)
        # remove train rectangles above the location rectangle
        dispObj.clearActionTrnRecs(loc, ydTrainNam)
        dispObj.drawTrain(ydTrainNam)
                
        if mVars.prms["dbgYdProc"]: print("train",ydTrainNam," starting: "
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

    def setTrnCoord(self, currLoc, trainStem):
        routeLen = routeCls.routes[currLoc]["rtLength"]
        trainStem["coord"]["yRoute"] = 0 # by definition rotated coord system is
            # along xRoute axis
        xRoute = trainStem["coord"]["xTrnInit"]*routeLen
        if trainStem["direction"] == "west":
                xRoute = -xRoute
        trainStem["coord"]["xRoute"] = xRoute    
        return 

