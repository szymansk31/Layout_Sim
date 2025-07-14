import random
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from display import dispItems
from yardCalcs import ydCalcs
from swCalcs import swArea
from gui import gui
np.set_printoptions(precision=2, suppress=True) 


dbgLocal = 1     
#=================================================
class locProc():
    
    def __init__(self):
        #self.locProcObj = locProc()
        pass
    
    #classmethod:
    
    def initLocDicts(self):
        from fileProc import readFiles
        files = readFiles()
        print("initializing location dicts: ")
        locs.locDat = files.readFile("locationFile")
        for loc in locs.locDat:
            self.countCars(loc)
        
    def countCars(self, loc):
        locDictStem = locs.locDat[loc]
        for dest in locDictStem["trackTots"]:
            #print("\n Location: ", loc, "destination: ", dest)
            for carType in locDictStem["tracks"][dest]:
                locDictStem["trackTots"][dest] = locDictStem["trackTots"][dest]\
                    + locDictStem["tracks"][dest][carType]
                #print("countCars: ", locDictStem)

    def locDests(self, loc):
        thisLocDests = []
        for dest in locs.locDat[loc]["trackTots"]:
            thisLocDests.append(dest)
        return thisLocDests

    def LocCalcs(self, thisLoc, loc):
        disp = dispItems()
        ydCalcObj = ydCalcs()
        swAreaObj = swArea()

        if mVars.prms["dbgYdProc"]: print("entering yardCalcs: locdat: "
                    , locs.locDat[loc])

        #if mVars.prms["\ndbgYdProc"]: print("yardCalcs: thisLoc ", thisloc)
        self.analyzeTrains(loc)
        if mVars.prms["dbgYdProc"]: print("trains analyzed: trainDB.ydTrains: ", trainDB.ydTrains)

        match thisLoc[loc]["type"]:
            case "yard":
                ydCalcObj.yardMaster(thisLoc, loc)
            case "swArea":
                swAreaObj.switchArea(thisLoc, loc)

                    
        disp.dispTrnInLoc(loc, trainDB.ydTrains)
            
    def analyzeTrains(self, loc):
        trainDB.ydTrains = {"brkDnTrn": [], "swTrain": [], "buildTrain": [], "roadCrewSw": []}

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
                case "switch" | "turn":
                    # for switch areas no yards
                    # code is in locProc but actions are undertaken by
                    # the virtual train crew
                    if trainNam not in trainDB.ydTrains["roadCrewSw"]:
                        trainDB.ydTrains["roadCrewSw"].append(trainNam)
                    pass
        
                
    def findRoutes(self, loc, ydTrainNam):
        for routeNam in routeCls.routes:
            loc = ''.join(loc)
            dest = ''.join(trainDB.trains[ydTrainNam]["nextLoc"])
            if dbgLocal: print("routNam: ", routeNam, " loc: ", loc, 
                " nextLoc: ", dest, "route: ", routeCls.routes[routeNam])
            if (loc in routeCls.routes[routeNam].values()) and \
                (dest in routeCls.routes[routeNam].values()):
                return routeNam

    def startTrain(self, action, loc, ydTrainNam):
        # setup train
        from trainProc import trainParams

        trainStem = trainDB.trains[ydTrainNam]
        dest = trainDB.trains[ydTrainNam]["nextLoc"]
        match dest:
            case dest if dest != "none":
                trainStem["status"] = "ready2Leave"
                # setup new route
                route4newTrn = self.findRoutes(loc, ydTrainNam)

                leftObj = routeCls.routes[route4newTrn]["leftObj"]
                rtObj = routeCls.routes[route4newTrn]["rtObj"]
                routeCls.routes[route4newTrn]["trains"].append(ydTrainNam)
                if loc == leftObj.strip(): 
                    trainStem["direction"] = "east"
                    trainStem["xTrnInit"] = gui.guiDict[loc]["x1"]
                elif loc == rtObj.strip():
                    trainStem["direction"] = "west"
                    trainStem["xTrnInit"] = gui.guiDict[loc]["x0"] - trainParams.trnLength
                else: print("no route found", ydTrainNam,  "leftObj: ", leftObj, "rtObj: "
                            , rtObj,"loc: ", loc, "direction: ", trainStem["direction"])

                trainStem["currentLoc"] = route4newTrn
                
            case "none":
                trainStem["status"] = "stop"
                
        if mVars.prms["dbgYdProc"]: print("train",ydTrainNam," built: "
            ,trainStem, ", route: ", routeCls.routes[route4newTrn])
        self.rmTrnFromLoc(action, loc, ydTrainNam)

    def rmTrnFromLoc(self, action, loc, ydTrainNam):
        # remove train from ydTrains and location
        print("rmTrnFromLoc: trainDB.ydTrains: ", trainDB.ydTrains)
        index = trainDB.ydTrains[action].index(ydTrainNam)
        trainDB.ydTrains[action].pop(index)
        if dbgLocal: print("after removal: trainDB.ydTrains: ", trainDB.ydTrains, 
                "\n trains[ydTrainNam]: ", trainDB.trains[ydTrainNam])
        
        index = locs.locDat[loc]["trains"].index(ydTrainNam)
        locs.locDat[loc]["trains"].pop(index)
        
