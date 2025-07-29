import random
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from display import dispItems
from yardCalcs import ydCalcs
from swCalcs import swCalcs
from stagCalcs import stCalcs
from gui import gui
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
        for carLoc in locStem["trackTots"]:
            print("\n Location: ", loc, "destination: ", carLoc)
            if carLoc not in trackStem: continue
            match type:
                case "yard":
                    locStem["trackTots"][carLoc] = sum(trackStem[carLoc].values())
                case "swArea":
                    locStem["trackTots"][carLoc] = \
                        sum(trackStem[carLoc]["pickups"].values()) + \
                        sum(trackStem[carLoc]["leave"].values()) 
        #print("countCars: ", locStem)
        locStem["totCars"] = sum(locStem["trackTots"].values())
                        

    def locDests(self, loc):
        thisLocDests = []
        for dest in locs.locDat[loc]["trackTots"]:
            thisLocDests.append(dest)
        return thisLocDests

    def printydTrains(self):
        if mVars.prms["dbgYdProc"]: print("trains analyzed: trainDB.ydTrains: ",
                    trainDB.ydTrains)
        
    def locCalcs(self, thisLoc, loc):
        disp = dispItems()
        ydCalcObj = ydCalcs()
        swAreaObj = swCalcs()
        stagCalcObj = stCalcs()

        if mVars.prms["dbgYdProc"]: 
            print("\nentering locCalcs: location: ", loc, ", locDat: ", locs.locDat[loc])

        thisLoc[loc]["totCars"] = sum(thisLoc[loc]["trackTots"].values())

        match thisLoc[loc]["type"]:
            case "yard":
                self.analyzeTrains(loc)
                self.printydTrains()
                ydCalcObj.yardMaster(thisLoc, loc)
            case "swArea":
                swAreaObj.swAnalyzeTrains(loc)
                self.printydTrains()
                swAreaObj.switchArea(thisLoc, loc)
            case "staging":
                stagCalcObj.stAnalyzeTrains(loc)
                self.printydTrains()
                stagCalcObj.staging(thisLoc, loc)

                    
        #disp.dispTrnLocDat(loc)
            
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
                    if trainNam not in trainDB.ydTrains["continue"]:
                        trainDB.ydTrains["continue"].append(trainNam)

                    self.startTrain("continue", loc, trainNam)
                case "built":
                    startTime = locs.locDat[loc]["bldTrnDepTimes"][0]
                    if mVars.time >= startTime - 1:
                        locs.locDat[loc]["bldTrnDepTimes"].pop(0)
                        nextLoc = trainDB.trains[trainNam]["nextLoc"]
                        print(trainNam, ": with start time ", startTime,
                              " in loc: ", loc, 
                              " built and leaving for (nextLoc): ", 
                              nextLoc)
                        # train status is "built"; use "noAction" to bypass
                        # train removal from ydTrains
                        self.startTrain("noAction", loc, trainNam)
        
                
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

    def startTrain(self, action, loc, ydTrainNam):
        # setup train
        from trainProc import trainParams
        disp = dispItems()

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
                else: 
                    print("no route found", ydTrainNam,  "leftObj: ", leftObj, "rtObj: "
                            , rtObj,"loc: ", loc, "direction: ", trainStem["direction"])
                    trainStem["status"] = "stop"
                    
                trainStem["firstDispTrn"] = 1
                trainStem["currentLoc"] = route4newTrn
                #print("trainStem: ", trainStem, ", original dict: ", trainDB.trains[ydTrainNam])
                disp.drawTrain(ydTrainNam)
            case "none":
                trainStem["status"] = "stop"
                
        if mVars.prms["dbgYdProc"]: print("train",ydTrainNam," starting: "
            ,trainStem, ",\n route: ", routeCls.routes[route4newTrn])
        self.rmTrnFromLoc(action, loc, ydTrainNam)

    def rmTrnFromLoc(self, action, loc, ydTrainNam):
        # remove train from ydTrains and location
        print("rmTrnFromLoc: trainDB.ydTrains: ", trainDB.ydTrains)
        if action == "noAction":
            print("Train no longer in ydTrains and waiting to leave")
        else:
            index = trainDB.ydTrains[action].index(ydTrainNam)
            trainDB.ydTrains[action].pop(index)
            if dbgLocal: print("after removal: trainDB.ydTrains: ", trainDB.ydTrains, 
                    "\n trains[ydTrainNam]: ", trainDB.trains[ydTrainNam])
        
        index = locs.locDat[loc]["trains"].index(ydTrainNam)
        locs.locDat[loc]["trains"].pop(index)
        
