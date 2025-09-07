import numpy as np
from mainVars import mVars
from trainInit import trainInit
from stateVars import locs, dspCh, trainDB, routeCls
from fileProc import readFiles
from display import dispItems
files = readFiles()
np.set_printoptions(precision=2, suppress=True) 


dbgLocal = 1   

#=================================================
class schedProc():

    def __init__(self):
        from locBase import locBase, Qmgmt, locMgmt
        self.locMgmtObj = locMgmt()
        self.trainInitObj = trainInit()
        self.dispItemsObj = dispItems()
        pass
    
    def initSchedule(self):
        # include starting trains
        dspCh.sched.update(files.readFile("startingTrainFile"))
        trainDB.consists.update(files.readFile("startingConsistFile"))
        dspCh.sched.update(files.readFile("scheduleFile"))
        print("\ninitSchedule: starting trains: ", dspCh.sched)

    def fetchLocSchedItem(self, loc):
        for trainNam in dspCh.sched:
            currentLoc = dspCh.sched[trainNam]["currentLoc"]
            if (loc == dspCh.sched[trainNam]["origLoc"]) and \
                (mVars.time >= dspCh.sched[trainNam]["startTime"]):
                self.baseTrnDict(trainNam)
                self.trainInitObj.fillTrnDicts(loc, trainNam)
                self.locMgmtObj.placeTrain(currentLoc, trainDB.trains[trainNam], 
                        trainNam)
                self.dispItemsObj.drawTrain(trainNam)
                dspCh.sched.pop(trainNam)
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
      
    def addTrn2Sched(self, loc, finalLoc):
        trainDB.numTrains +=1
        newTrainNum = trainDB.numTrains
        newTrainNam = "train" + str(newTrainNum)
        dspCh.sched.update ({
          newTrainNam: {
            "origLoc": loc,
            "currentLoc": loc,
            "finalLoc": finalLoc,
            "status":"init",
            "startTime": mVars.time
          }
        })
        print("added train to sched:", newTrainNam, "params:", dspCh.sched[newTrainNam])

    
#=================================================
#=================================================
class clearTrnCalcs():
    
    def __init__(self):
        from locBase import locBase, Qmgmt, locMgmt
        self.locMgmtObj = locMgmt()
        self.locBaseObj = locBase()
        self.QmgmtObj = Qmgmt()
        from routeProc import rtCaps, routeMgmt
        self.rtCapsObj = rtCaps()
        pass
                   
    def mainDispatch(self):
        # look at all trains on routes and
        # determine if they will soon reach a loc
        self.rtCapsObj.printRtCaps()
        self.QmgmtObj.calcDeptTimes()
        self.QmgmtObj.calcArrivTrns()
        self.QmgmtObj.updateArrvQs()
        self.QmgmtObj.sortLocQ("arrivals", "estArrTime")
        self.assnArrTrks()
        # are 

    def clearTrn(self, loc, trainNam):
        QStem = locs.locDat[loc]["Qs"]["arrivals"]
        arrTrkAssnd = False
        QDict = [QDict for idx, QDict in enumerate(QStem) if trainNam in QDict]
        rtClear = self.rtCapsObj.checkRtSlots(trainNam)
        if QDict[0][trainNam]["arrTrk"] != "": arrTrkAssnd = True
        print("clearTrn: rtClear = ", rtClear, " , arrTrkAssnd = ", arrTrkAssnd)
        return rtClear and arrTrkAssnd
        
# trains already on routes get first priority to arrival slots
# as opposed to trains being built at other locs for travel to this loc                
    
    def assnArrTrks(self):
        for loc in locs.locDat:
            trkStem = locs.locDat[loc]["trkPrms"]
            QStem = locs.locDat[loc]["Qs"]["arrivals"]
            idx = -1
            for QDict in QStem:
                idx +=1
                print("assnArrTrk; loc:", loc, "QDict:", QDict)
                inComTrnNam = next(iter(QDict))
                estArrTime = QDict[inComTrnNam]["estArrTime"]
                if QDict[inComTrnNam]["arrTrk"] != "": continue
                for trackNam in trkStem:
                    if ("arrival" in trkStem[trackNam]["funcs"]):
                        match trkStem[trackNam]["status"]:
                            case "unAssnd":
                                self.addTrain2ArrTrack(loc, trackNam, inComTrnNam)
                                break
                            case "assnd" if self.checkDepTime(loc, trackNam, estArrTime):
                                trkStem[trackNam]["status"] = "assnAtDep"
                                QStem[idx][inComTrnNam]["arrTrk"] = trackNam
                                break
                            case "assnAtDep":
                                self.procAssnAtDep(loc, trkStem, trackNam, inComTrnNam)
                                break
                if QDict[inComTrnNam]["arrTrk"] == "":
                    print("no arrival track available for train: ", inComTrnNam, " in loc: ", loc)
                                
    def procAssnAtDep(self, loc, trkStem, trackNam, inComTrnNam):
        #check if train approaching loc and arrTrk still blocked

        trnOnArrTrk = trkStem[trackNam]["train"]
        inComTrnStem = trainDB.trains[inComTrnNam]
        inComTrnLoc = inComTrnStem["currentLoc"]
        if "route" not in inComTrnLoc: return
        
        rtLength = routeCls.routes[inComTrnLoc]["rtLength"]
        fracRtRemaining = 1 - inComTrnStem["coords"]["xRoute"]/rtLength
        if fracRtRemaining <= 0.25:
            rtTransTime = routeCls.routes[inComTrnLoc]["transTime"]
            timeRemaining = fracRtRemaining*rtTransTime
            estArrTime = mVars.time + timeRemaining
            if self.checkDepTime(loc, trackNam, estArrTime):
                print("assnAtDep; loc:", loc, "incoming route", inComTrnLoc, "trnOnArrTrk:", 
                    trnOnArrTrk, "rtLength:", rtLength, "incoming train status:",
                    inComTrnStem["status"])
                if inComTrnStem["status"] == "waitOnRoute":
                    inComTrnStem["status"] = "enroute"
                return
            else: 
                inComTrnStem["status"] = "waitOnRoute"
                return

    def addTrain2ArrTrack(self, loc, arrTrk, trainNam):
        QStem = locs.locDat[loc]["Qs"]["arrivals"]
        print("adding train ", trainNam, " to arr track: ", arrTrk, "in loc ", loc)
        idx = [idx for idx, QDict in enumerate(QStem) if trainNam in QDict]
        locStem = locs.locDat[loc]["trkPrms"]
        trnStem = trainDB.trains[trainNam]
        
        print("idx, QStem: ", idx, " ,", QStem)
        locStem[arrTrk]["train"] = trainNam
        locStem[arrTrk]["status"] = "assnd"
        trnStem["arrTrk"] = arrTrk
        trnStem["estDeptTime"] = trnStem["estArrTime"] + trainDB.avgSwTime
        QStem[idx[0]][trainNam]["arrTrk"] = arrTrk

        locs.locDat[loc]["trkCounts"]["openArrTrks"] -=1
        pass
    


    def checkDepTime(self, loc, track, estArrTime):
        trnOnArrTrk = locs.locDat[loc]["trkPrms"][track]["train"]
        estDeptTime = trainDB.trains[trnOnArrTrk]["estDeptTime"]
        print("checking track:", track, ", assnd to train:", trnOnArrTrk,"at loc:", loc, ", estArrTime: ", estArrTime, "for train departing: ", estDeptTime)
        if estArrTime > estDeptTime: return True
        else: return False
        
    
