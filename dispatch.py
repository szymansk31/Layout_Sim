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
    routeCap = {}
    
    def __init__(self):
        pass
    
class rtCaps():
    rtCap = {}
    
    def __init__(self):
        pass
    
    def initRouteCaps(self):
        rtCaps.rtCap = files.readFile("routeCapFile")
        for route in rtCaps.rtCap:
                   
            pass
    
    def updateRtSlots(self):
        for route in rtCaps.rtCap:
            # trains already on the route
            rtStem = rtCaps.rtCap[route]
            eastSlots = 0
            westSlots = 0
            numEast = rtStem["numEastTrns"]
            numWest = rtStem["numWestTrns"]
            if numEast == 0 and numWest == 0:
                eastSlots = max(rtStem["sameDirMonoCap"], 0)
                westSlots = eastSlots
            elif numEast != 0 and numWest == 0:
                eastSlots = max(rtStem["sameDirMonoCap"] - numEast, 0)
                westSlots = max(rtStem["oppoDirCap"] - numWest, 0)
            elif numEast == 0 and numWest != 0:
                westSlots = max(rtStem["sameDirMonoCap"] - numWest, 0)
                eastSlots = max(rtStem["oppoDirCap"] - numEast, 0)
            elif numEast != 0 and numWest != 0:
                if (numEast < rtStem["sameDirBiCap"]) and \
                    (numWest <= rtStem["oppoDirCap"]):
                    eastSlots = max(rtStem["sameDirBiCap"] - numEast, 0)
                    westSlots = max(rtStem["oppoDirCap"] - numWest, 0)
                elif (numWest < rtStem["sameDirBiCap"]) and \
                    (numEast <= rtStem["oppoDirCap"]):
                    westSlots = max(rtStem["sameDirBiCap"] - numWest, 0)
                    eastSlots = max(rtStem["oppoDirCap"] - numEast, 0)

            rtStem["eastSlots"] = eastSlots
            rtStem["westSlots"] = westSlots                    

    def updateRtSlots2(self):
        for route in rtCaps.rtCap:
            # trains already on the route
            rtStem = rtCaps.rtCap[route]
            numEast = rtStem["numEastTrns"]
            numWest = rtStem["numWestTrns"]
            biDirBit = False
            biDirBit = True
            if numEast == 0 and numWest == 0:
                eastSlots = max(rtStem["sameDirMonoCap"], 0)
                westSlots = eastSlots
                eastSlots = max(rtStem[False]["sameDirCap"] - numEast, 0)
                westSlots = max(rtStem[False]["sameDirCap"] - numWest, 0)
            elif numEast != 0 and numWest == 0:
                eastSlots = max(rtStem["sameDirMonoCap"] - numEast, 0)
                westSlots = max(rtStem["oppoDirCap"] - numWest, 0)
                eastSlots = max(rtStem[False]["sameDirCap"] - numEast, 0)
                westSlots = max(rtStem[True]["oppoDirCap"] - numWest, 0)
            elif numEast == 0 and numWest != 0 :
                westSlots = max(rtStem["sameDirMonoCap"] - numWest, 0)
                eastSlots = max(rtStem["oppoDirCap"] - numEast, 0)
                eastSlots = max(rtStem[True]["oppoDirCap"] - numEast, 0)
                westSlots = max(rtStem[False]["sameDirCap"] - numWest, 0)
            elif numEast != 0 and numWest != 0:
                if (numEast < rtStem["sameDirBiCap"]) and \
                    (numWest <= rtStem["oppoDirCap"]):
                    eastSlots = max(rtStem["sameDirBiCap"] - numEast, 0)
                    westSlots = max(rtStem["oppoDirCap"] - numWest, 0)
                elif (numWest < rtStem["sameDirBiCap"]) and \
                    (numEast <= rtStem["oppoDirCap"]):
                    WestSlots = max(rtStem["sameDirBiCap"] - numWest, 0)
                    eastSlots = max(rtStem["oppoDirCap"] - numEast, 0)
                eastSlots = max(rtStem[True]["oppoDirCap"] - numEast, 0)
                westSlots = max(rtStem[True]["oppoDirCap"] - numWest, 0)

            rtStem["biDir"]                    

    def fillTrnsOnRoute(self, routeNam, trainNam):
        routeStem = routeCls.routes[routeNam]["trains"]
        routeStem.append(trainNam)
        dir = trainDB.trains[trainNam]["direction"]
        if "ea" in dir:
            rtCaps.rtCap[routeNam]["numEastTrns"] +=1
        else:
            rtCaps.rtCap[routeNam]["numWestTrns"] +=1
       
    def remTrnsOnRoute(self, routeNam, trainNam):
        routeStem = routeCls.routes[routeNam]["trains"]
        try:
            index = routeStem.index(trainNam)
            routeStem.pop(index)
        except:
            pass
        
        dir = trainDB.trains[trainNam]["direction"]
        numEast = rtCaps.rtCap[routeNam]["numEastTrns"]
        numWest = rtCaps.rtCap[routeNam]["numWestTrns"]
        if dir == "east":
            num = max(numEast -1, 0)
            rtCaps.rtCap[routeNam]["numEastTrns"] = num
        else:
            num = max(numWest -1, 0)
            rtCaps.rtCap[routeNam]["numWestTrns"] = num
        
       