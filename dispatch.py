import random
import numpy as np
from mainVars import mVars
from stateVars import locs, dspCh, trainDB, routeCls
from display import dispItems
from yardCalcs import ydCalcs
from swCalcs import swCalcs
from stagCalcs import stCalcs
from gui import gui
from fileProc import readFiles

np.set_printoptions(precision=2, suppress=True) 


dbgLocal = 1   

#=================================================
class schedProc():

    def __init__(self):
        pass
    
    def initSchedule(self):
        # include starting trains
        for train in trainDB.strtTrns:
            dspCh.sched[train] = \
                    {
                "startTime":
                trainDB.trains[train]["startTime"],
                "status":
                trainDB.trains[train]["status"],
                "action":
                trainDB.trains[train]["status"],
                "finalLoc": 
                trainDB.trains[train]["finalLoc"],
                "origLoc": 
                trainDB.trains[train]["origLoc"],
                "currentLoc": 
                trainDB.trains[train]["currentLoc"],
                "nextLoc": 
                trainDB.trains[train]["nextLoc"],
                "stops":
                trainDB.trains[train]["stops"]
                    }

        files = readFiles()
        dspCh.sched.update(files.readFile("scheduleFile"))
        print("\ninitSchedule: starting trains: ", dspCh.sched)

    def fetchLocSchedItem(self, loc):
        from locProc import locBase
        for train in dspCh.sched:
            if (loc == dspCh.sched[train]["origLoc"]) and \
                (mVars.time >= dspCh.sched[train]["startTime"]):
                action = dspCh.sched[train]["action"]
                trainDB.ydTrains[action].append(train)
                locBase.addTrn2Loc(loc, train)
                return
            pass
    
#=================================================
class dspchProc():
    
    def __init__(self):
        pass
    
    def initDspchDicts(self):
        files = readFiles()
        print("initializing dispatch dicts: ")
        dspCh.dspchDat = files.readFile("dspchDatFile")

        # map dspchDat onto loc dicts for common data
        for loc in dspCh.dspchDat:
            dspCh.dspchDat["totCars"] = locs.locDat[loc]["totCars"]
            dspCh.dspchDat["numAdjLocs"] = locs.locDat[loc]["numAdjLocs"]
            dspCh.dspchDat["adjLocNames"] = locs.locDat[loc]["adjLocNames"]
            dspCh.dspchDat["trains"] = locs.locDat[loc]["trains"]
            dspCh.dspchDat["bldTrnDepTimes"] = locs.locDat[loc]["bldTrnDepTimes"]
            
