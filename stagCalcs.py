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
        from locBase import locBase, Qmgmt, locMgmt
        self.locBaseObj = locBase()
        self.locQmgmtObj = Qmgmt()
        self.locMgmtObj = locMgmt()
        from classCars import classCars
        self.classObj = classCars()
        from display import dispItems
        self.dispObj = dispItems()
        from trainProc import trnProc
        self.trnProcObj = trnProc()

    def staging(self, loc):
        
        for trainNam in trainDB.ydTrains["wait4Clrnce"]:
            if mVars.time == trainDB.trains[trainNam]["startTime"]:
                nextLoc = trainDB.trains[trainNam]["nextLoc"]

                print("in staging: nextLoc: ", nextLoc)
                locs.locDat[loc]["trnCnts"]["started"] += 1

                self.locMgmtObj.rmTrnFrmActions("wait4Clrnce", loc, trainNam)
                self.locProcObj.startTrain(loc, trainNam)
                
        self.dispObj.dispTrnLocDat(loc)
                
    def stAnalyzeTrains(self, loc):
        trainDB.ydTrains = {"wait4Clrnce": [], "terminated": [], "turn": []}

        # train status leads to actions by the yard crew or
        # the train crew.  Train actions are the same name as
        # the corresponding train status string
        for trainNam in locs.locDat[loc]["trains"]:
            match trainDB.trains[trainNam]["status"]:
                case "wait4Clrnce":
                    if trainNam not in trainDB.ydTrains["wait4Clrnce"]:
                        trainDB.ydTrains["wait4Clrnce"].append(trainNam)
                case "terminate":
                    self.dispObj.clearRouteTrnRecs(trainNam)
                    if trainNam not in trainDB.ydTrains["terminated"]:
                        trainDB.ydTrains["terminated"].append(trainNam)
