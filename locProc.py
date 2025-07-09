import random
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB
from display import dispObj
from yardCalcs import ydCalcs
from swCalcs import swArea
np.set_printoptions(precision=2, suppress=True) 


dbgLocal = 1     
#=================================================
class locProc():
    locs = locs()
    
    def __init__(self):
        self.thisConsist = {}
        self.ydTrains = {}
        
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
                

