import random
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from display import dispItems
from yardCalcs import ydCalcs
from swCalcs import swCalcs
from stagCalcs import stCalcs
from gui import gui
from coords import transForms
np.set_printoptions(precision=2, suppress=True) 


dbgLocal = 1     
#=================================================
class locProc():
    
    def __init__(self):
        pass
    
    #classmethod:
    
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
        match type:
            case "yard":
                trackStem = locStem["tracks"]
            case "swArea":
                trackStem = locStem["industries"]
        for trackNam in locStem["destTrkTots"]:
            print("\n Location: ", loc, "destination: ", trackNam)
            if trackNam not in trackStem: continue
            match type:
                case "yard":
                    locStem["destTrkTots"][trackNam] = sum(trackStem[trackNam].values())
                    locStem["totCars"] = sum(locStem["destTrkTots"].values())
                case "swArea":
                    if trackNam == "offspot": 
                        locStem["numOffspot"] = sum(locs.locDat[loc]["offspot"].values())
                        continue
                    locStem["indusTots"][trackNam] = \
                        sum(trackStem[trackNam]["pickups"].values()) + \
                        sum(trackStem[trackNam]["leave"].values())
                    locStem["totCars"] = sum(locStem["indusTots"].values())
                    locStem["totCars"] += locStem["numOffspot"]
                    
        #print("countCars: ", locStem)
                        

    def locDests(self, loc):
        thisLocDests = []
        for dest in locs.locDat[loc]["destTrkTots"]:
            thisLocDests.append(dest)
        return thisLocDests

    def printydTrains(self):
        if mVars.prms["dbgYdProc"]: print("trains analyzed: trainDB.ydTrains: ",
                    trainDB.ydTrains)
        
    def locCalcs(self, thisLoc, loc):
        ydCalcObj = ydCalcs()
        swAreaObj = swCalcs()
        stagCalcObj = stCalcs()

        if mVars.prms["dbgYdProc"]: 
            print("\nentering locCalcs: location: ", loc, ", locDat: ", locs.locDat[loc])

        thisLoc[loc]["totCars"] = sum(thisLoc[loc]["destTrkTots"].values())

        match thisLoc[loc]["type"]:
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
                case "building":
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
                    self.startTrain(loc, trainNam)
                case "built":
                    startTime = locs.locDat[loc]["bldTrnDepTimes"][0]
                    if mVars.time >= startTime - 1:
                        locs.locDat[loc]["bldTrnDepTimes"].pop(0)
                        nextLoc = trainDB.trains[trainNam]["nextLoc"]
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
            #if dbgLocal: print("routNam: ", routeNam, " loc: ", loc, 
            #    " nextLoc: ", dest, "route: ", routeCls.routes[routeNam])
            if (loc in routeCls.routes[routeNam].values()) and \
                (dest in routeCls.routes[routeNam].values()):
                return routeNam

    def startTrain(self, loc, ydTrainNam):
        # setup train
        from trainProc import trainParams
        dispObj = dispItems()
        coordObj = transForms()

        trainStem = trainDB.trains[ydTrainNam]
        dest = trainDB.trains[ydTrainNam]["nextLoc"]
        match dest:
            case dest if dest != "none":
                trainStem["status"] = "ready2Leave"
                # setup new route
                route4newTrn = self.findRoutes(loc, ydTrainNam)

                leftObj = routeCls.routes[route4newTrn]["leftObj"].strip()
                rtObj = routeCls.routes[route4newTrn]["rtObj"].strip()
                routeCls.routes[route4newTrn]["trains"].append(ydTrainNam)
                if loc == leftObj: 
                    trainStem["direction"] = "east"
                elif loc == rtObj:
                    trainStem["direction"] = "west"
                else: 
                    print("no route found", ydTrainNam,  "leftObj: ", leftObj, "rtObj: "
                            , rtObj,"loc: ", loc, "direction: ", trainStem["direction"])
                    trainStem["status"] = "stop"
                    
                trainStem["firstDispTrn"] = 1
                trainStem["currentLoc"] = route4newTrn
                
                #sets initial coords in rotated system    
                trainStem["coord"]["xTrnInit"] = 0  # train starting at location
                self.setTrnCoord(trainStem["currentLoc"], trainStem)                
                coordObj.xRoute2xPlot(route4newTrn, ydTrainNam)
                eastXPlot = gui.guiDict[loc]["x1"]
                westXPlot = gui.guiDict[loc]["x0"] - trainParams.trnLength
                eastYPlot = gui.guiDict[leftObj]["y0"] - gui.guiDict["locDims"]["height"]*0.25

                if trainStem["direction"] == "west": 
                    trainStem["coord"]["xPlot"] -= trainParams.trnLength
                    westXPlotTransform = trainStem["coord"]["xPlot"]
                print("test of coord transform: \neastXPlot no transform: ", eastXPlot, ", with transform: ", 
                     trainStem["coord"]["xPlot"])
                print("westXPlot no transform: ", westXPlot, ", with transform: ", 
                      westXPlotTransform)
                print("eastYPlot no transform: ", eastYPlot, ", with transform: ", 
                      trainStem["coord"]["yPlot"])

                #print("trainStem: ", trainStem, ", original dict: ", trainDB.trains[ydTrainNam])
                dispObj.drawTrain(ydTrainNam)
            case "none":
                trainStem["status"] = "stop"
                
        if mVars.prms["dbgYdProc"]: print("train",ydTrainNam," starting: "
            ,trainStem, ",\n")
            #route: ", routeCls.routes[route4newTrn])

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
    
    def rmTrnFrmLoc(self, loc, tranNam):  
        index = locs.locDat[loc]["trains"].index(tranNam)
        locs.locDat[loc]["trains"].pop(index)

    def setTrnCoord(self, currLoc, trainStem):

        routeLen = routeCls.routes[currLoc]["rtLength"]
        trainStem["coord"]["yRoute"] = 0 # by definition rotated coord system is
            # along xRoute axis
        xRoute = trainStem["coord"]["xTrnInit"]*routeLen
        if trainStem["direction"] == "west":
                xRoute = -xRoute
        trainStem["coord"]["xRoute"] = xRoute    
        return 

