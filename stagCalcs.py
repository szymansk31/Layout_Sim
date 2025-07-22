import random
from enum import Enum
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls

np.set_printoptions(precision=2, suppress=True) 

dbgLocal = 1          
class stCalcs():
    startMisc = 0
    ready2Pickup = 0

    def __init__(self):
        self.weights = [0.3, 0.3, 0.3, 0, 0]
        #self.weights = [0, 0, 0, 0, 0]
        from locProc import locProc
        self.locProcObj = locProc()
        from classCars import classCars
        self.classObj = classCars()
        from display import dispItems
        self.dispObj = dispItems()
        from trainProc import trnProc
        self.trnProcObj = trnProc()

    def staging(self, thisLoc, loc):
        
        self.stAnalyzeTrains(loc)
        if mVars.prms["dbgYdProc"]: print("trains analyzed: trainDB.ydTrains: ", trainDB.ydTrains)

        
        for train in trainDB.ydTrains["ready2Leave"]:
            if mVars.time == trainDB.trains[train]["startTime"] - 1:
                nextLoc = trainDB.trains[train]["nextLoc"]

                print("in staging: nextLoc: ", nextLoc)
                self.locProcObj.startTrain("ready2Leave", loc, train)
                
        self.dispObj.dispTrnLocDat(loc)
                
    def stAnalyzeTrains(self, loc):
        trainDB.ydTrains = {"ready2Leave": [], "terminated": []}

        # train status leads to actions by the yard crew or
        # the train crew.  Train actions are the same name as
        # the corresponding train status string
        for trainNam in locs.locDat[loc]["trains"]:
            match trainDB.trains[trainNam]["status"]:
                case "ready2Leave":
                    if trainNam not in trainDB.ydTrains["ready2Leave"]:
                        trainDB.ydTrains["ready2Leave"].append(trainNam)
                case "terminate":
                    if trainNam not in trainDB.ydTrains["terminated"]:
                        trainDB.ydTrains["terminated"].append(trainNam)
