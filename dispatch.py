import random
import numpy as np
from mainVars import mVars
from trainInit import trainInit
from stateVars import locs, dspCh, trainDB, routeCls
from fileProc import readFiles
files = readFiles()
np.set_printoptions(precision=2, suppress=True) 


dbgLocal = 1   

#=================================================
class schedProc():

    def __init__(self):
        pass
    
    def initSchedule(self):
        # include starting trains

        dspCh.sched.update(files.readFile("scheduleFile"))
        print("\ninitSchedule: starting trains: ", dspCh.sched)

    def fetchLocSchedItem(self, loc):
        from locProc import locBase
        trainInitObj = trainInit()
        for trainNam in dspCh.sched:
            if (loc == dspCh.sched[trainNam]["origLoc"]) and \
                (mVars.time >= dspCh.sched[trainNam]["startTime"]):
                locBase.addTrn2Loc_rt(loc, dspCh.sched[trainNam], trainNam)
                self.baseTrnDict(trainNam)
                dspCh.sched.pop(trainNam)
                trainInitObj.fillTrnDicts(loc, trainNam)
                return
            pass
        
    def baseTrnDict(self, trainNam):
        protoTrnDict = files.readFile("trainFile")
        #make sure train has all required keys, but no trainNam
        tmpTrain = protoTrnDict.pop("trnProtype")
        #overwrite proto values with vals from schedule
        tmpTrain.update(dspCh.sched[trainNam])
        print("baseTrnDict: protoTrnDict: ", tmpTrain)
        #trainDB key=train gets currently known info 
        # (may not be complete depending on detail in sched file
        # and starting trains file)
        trainDB.trains[trainNam] = tmpTrain
        
    
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
            
