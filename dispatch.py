import numpy as np
from mainVars import mVars
from trainInit import trainInit
from stateVars import locs, dspCh, trainDB, routeCls
from locBase import locBase, Qmgmt, locMgmt
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
        from locBase import locBase, Qmgmt, locMgmt
        locMgmtObj = locMgmt()
        trainInitObj = trainInit()
        for trainNam in dspCh.sched:
            if (loc == dspCh.sched[trainNam]["origLoc"]) and \
                (mVars.time >= dspCh.sched[trainNam]["startTime"]):
                locMgmtObj.addTrn2LocOrRt(loc, dspCh.sched[trainNam], 
                        trainNam)
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
#=================================================
class clearTrnCalcs():
    
    def __init__(self):
        self.locBaseObj = locBase()
        self.QmgmtObj = Qmgmt()
        pass
                   
    def mainDispatch(self):
        # look at all trains on routes and
        # determine if they will soon reach a loc
        self.QmgmtObj.calcArrivTrns()
        self.QmgmtObj.sortArrvQ()
        self.assnArrTrks()
        # are 

    def clearTrn(self, loc, trainNam):
        pass
    
    def assnArrTrks(self):
        for loc in locs.locDat:
            trkStem = locs.locDat[loc]["trkPrms"]
            
            QStem = locs.locDat[loc]["Qs"]["arrivals"]
            for trainNam in QStem:
                estArrTime = QStem[trainNam]["estArrTime"]
                for track in trkStem:
                    if (trkStem[track]["funcs"] == "arrival"):
                        match trkStem[track]["status"]:
                            case "unAssnd":
                                trkStem[track]["train"] = trainNam
                                trkStem[track]["status"] = "assnd"
                                QStem["arrTrk"] = track
                                break
                            case "assnd" if self.checkDepTime(loc, track, estArrTime):
                                trkStem[track]["status"] = "assnAtDep"
                                QStem["arrTrk"] = track
                                
                                    
                print("no arrival track available for train: ", trainNam, " in loc: ", loc)

    def checkDepTime(self, loc, track, estArrTime):
        QStem = locs.locDat[loc]["Qs"]["departs"]
        estDepTime = [QStem[tNam]["estDepTime"] \
            for tNam in QStem if track == QStem[tNam]["depTrk"]]
        if estArrTime > estDepTime: return True
        
    
