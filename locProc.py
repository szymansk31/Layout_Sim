import random
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from display import dispObj
from yardCalcs import ydCalcs
from swCalcs import swArea
from gui import gui
from trainProc import trainParams
np.set_printoptions(precision=2, suppress=True) 


dbgLocal = 1     
#=================================================
class locProc():
    locs = locs()
    
    def __init__(self):
        self.ydTrains = {}
        #self.locProcObj = locProc()
        
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
        disp = dispObj()
        ydCalcObj = ydCalcs()
        swAreaObj = swArea()

        if mVars.prms["dbgYdProc"]: print("entering yardCalcs: locdat: "
                    , locs.locDat[loc])

        #if mVars.prms["\ndbgYdProc"]: print("yardCalcs: thisLoc ", thisloc)
        self.analyzeTrains(loc)
        if mVars.prms["dbgYdProc"]: print("trains analyzed: ydTrains: ", self.ydTrains)

        disp.dispLocDat(loc)
        match thisLoc[loc]["type"]:
            case "yard":
                ydCalcObj.yardMaster(thisLoc, loc, self.ydTrains)
            case "swArea":
                swAreaObj.switchArea(thisLoc, loc, self.ydTrains)

                    
        disp.dispTrnInLoc(loc, self.ydTrains)
            
    def analyzeTrains(self, loc):
        self.ydTrains = {"brkDnTrn": [], "swTrain": [], "buildTrain": [], "roadCrewSw": []}

        # train status leads to actions by the yard crew or
        # the train crew.  Train actions are the same name as
        # the corresponding train status string
        for trainNam in locs.locDat[loc]["trains"]:
            match trainDB.trains[trainNam]["status"]:
                case "terminate":
                    if trainNam not in self.ydTrains["brkDnTrn"]:
                        self.ydTrains["brkDnTrn"].append(trainNam)
                case "dropPickup":
                    # in a yard this action is often undertaken by 
                    # the yard crew; hence a yard action
                    if trainNam not in self.ydTrains["swTrain"]:
                        self.ydTrains["swTrain"].append(trainNam)
                case "building":
                    # for yards, not switch areas
                    if trainNam not in self.ydTrains["buildTrain"]:
                        self.ydTrains["buildTrain"].append(trainNam)
                case "switch" | "turn":
                    # for switch areas no yards
                    # code is in locProc but actions are undertaken by
                    # the virtual train crew
                    if trainNam not in self.ydTrains["roadCrewSw"]:
                        self.ydTrains["roadCrewSw"].append(trainNam)
                    pass
                
    def findRoutes(self, loc, ydtrainNam):
        for routeNam in routeCls.routes:
            loc = ''.join(loc)
            dest = ''.join(trainDB.trains[ydtrainNam]["nextLoc"])
            if dbgLocal: print("routNam: ", routeNam, " loc: ", loc, 
                " nextLoc: ", dest, "route: ", routeCls.routes[routeNam])
            if (loc in routeCls.routes[routeNam].values()) and \
                (dest in routeCls.routes[routeNam].values()):
                return routeNam

    def startTrain(self, loc, ydtrains, ydtrainNam):
        # setup train
        trainStem = trainDB.trains[ydtrainNam]
        dest = trainDB.trains[ydtrainNam]["nextLoc"]
        match dest:
            case dest if dest != "none":
                trainStem["status"] = "ready2Leave"
                # setup new route
                route4newTrn = self.findRoutes(loc, ydtrainNam)

                leftObj = routeCls.routes[route4newTrn]["leftObj"]
                rtObj = routeCls.routes[route4newTrn]["rtObj"]
                routeCls.routes[route4newTrn]["trains"].append(ydtrainNam)
                if loc == leftObj.strip(): 
                    trainStem["direction"] = "east"
                    trainStem["xTrnInit"] = gui.guiDict[loc]["x1"]
                elif loc == rtObj.strip():
                    trainStem["direction"] = "west"
                    trainStem["xTrnInit"] = gui.guiDict[loc]["x0"] - trainParams.trnLength
                else: print("built train", ydtrainNam,  "leftObj: ", leftObj, "rtObj: "
                            , rtObj,"loc: ", loc, "direction: ", trainStem["direction"])

                trainStem["currentLoc"] = route4newTrn
                
            case "none":
                trainStem["status"] = "stop"
                
        if mVars.prms["dbgYdProc"]: print("train",ydtrainNam," built: "
            ,trainStem, ", route: ", routeCls.routes[route4newTrn])
        self.rmTrnFromLoc("buildTrain", loc, ydtrains, ydtrainNam)

    def rmTrnFromLoc(self, action, loc, ydtrains, ydtrainNam):
        print("rmTrnFromLoc: ydtrains: ", ydtrains)
        index = ydtrains[action].index(ydtrainNam)
        ydtrains[action].pop(index)
        if dbgLocal: print("after removal: ydTrains: ", ydtrains, 
                "\n trains[ydtrainNam]: ", trainDB.trains[ydtrainNam])
        
        index = locs.locDat[loc]["trains"].index(ydtrainNam)
        locs.locDat[loc]["trains"].pop(index)
        
