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
                locMgmtObj.placeTrain(loc, dspCh.sched[trainNam], 
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
            idx = -1
            for QDict in QStem:
                idx +=1
                trainNam = next(iter(QDict))
                estArrTime = QDict[trainNam]["estArrTime"]
                if QDict[trainNam]["arrTrk"] != "": continue
                for track in trkStem:
                    if ("arrival" in trkStem[track]["funcs"]):
                        match trkStem[track]["status"]:
                            case "unAssnd":
                                self.addTrain2ArrTrack(loc, track, trainNam)
                                break
                            case "assnd" if self.checkDepTime(loc, track, estArrTime):
                                trkStem[track]["status"] = "assnAtDep"
                                QStem[idx][trainNam]["arrTrk"] = track
                print("no arrival track available for train: ", trainNam, " in loc: ", loc)
                                
    def addTrain2ArrTrack(self, loc, track, trainNam):
        QStem = locs.locDat[loc]["Qs"]["arrivals"]
        idx = [idx for idx, QDict in enumerate(QStem) if track in QDict]
        locStem = locs.locDat[loc]["trkPrms"]
        trnStem = trainDB.trains[trainNam]
        
        locStem[track]["train"] = trainNam
        locStem[track]["status"] = "assnd"
        trnStem["arrTrk"] = track
        QStem[idx][trainNam]["arrTrk"] = track

        locs.locDat[loc]["trkCounts"]["openArrTrks"] -=1
        pass
    
                                    

    def checkDepTime(self, loc, track, estArrTime):
        QStem = locs.locDat[loc]["Qs"]["departs"]
        estDepTime = [QStem[idx][next(iter(QDict))]["estDepTime"] \
            for idx, QDict in enumerate(QStem) if track in QDict]
        # no train on this track (not in "departs" Q), but assigned
        # to incoming train - therefore return false
        if len(estDepTime) == 0: return False
        if estArrTime > estDepTime[0]: return True
        else: return False
        
    
