import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from dispatch import clearTrnCalcs
from fileProc import readFiles
files = readFiles()

np.set_printoptions(precision=2, suppress=True) 

class routeInit():
    
    def __init__(self):
        pass
    
class rtProc():
    
    def __init__(self):
        from outputMethods import printMethods, statSave
        self.printObj = printMethods()
        from trainProc import trnProc
        self.trnProcObj = trnProc()
        self.rtCapsObj = rtCaps()
        self.rtMgmtObj = routeMgmt()
        self.clrTrnObj = clearTrnCalcs()
        from display import dispItems
        self.dispObj = dispItems()
        from locBase import locBase, Qmgmt, locMgmt
        self.locBaseObj = locBase()
        self.locQmgmtObj = Qmgmt()
        self.locMgmtObj = locMgmt()
        pass
    
    def routeProc(self):
        self.rtCapsObj.updateRtSlots()
        self.rtCapsObj.printRtCaps()

        for routeNam in routeCls.routes:
            rtStem = routeCls.routes[routeNam]["trains"]
            self.procRouteQ(routeNam)
            for trainNam in rtStem:
                if mVars.time >= trainDB.trains[trainNam]["startTime"]:
                    self.printObj.printTrainInfo(trainNam)
                    self.trnProcObj.trainCalcs(trainDB.trains[trainNam], trainNam)
        
    def procRouteQ(self, routeNam):
        rtStem = rtCaps.rtCap[routeNam]["Q"]
        for trainNam in rtStem:
            trnStem = trainDB.trains[trainNam]
            if (trnStem["status"] == "wait4Clrnce") and \
                (self.clrTrnObj.clearTrn(trnStem["nextLoc"], trainNam)):
                trnStem["status"] = "enroute"
                trnStem["currentLoc"] = trnStem["rtToEnter"]
                self.rtMgmtObj.addTrn2Route(trnStem["currentLoc"], trainNam)
                self.rtCapsObj.remTrnFrmRouteQ(routeNam, trainNam)
                self.dispObj.drawTrain(trainNam)
                self.cleanTrnFromLoc(trainNam)
                print(trainNam, "added to route", routeNam, "with enroute status")
         
    def cleanTrnFromLoc(self, trainNam):
        loc = trainDB.trains[trainNam]["departStop"]
        if loc != "":
            arrTrk = self.locQmgmtObj.readArrTrk(loc, trainNam)
            #remove train from location arrivals Queue
            self.locQmgmtObj.remTrnLocQ(loc, "arrivals", trainNam)
            #remove train from loc["trkPrms"]["arrTrk"]
            self.locQmgmtObj.remTrnArrTrk(loc, arrTrk, trainNam)
            #remove train from loc["trains"] list
            self.locMgmtObj.rmTrnFrmLoc(loc, trainNam)
            #remove train rectangle from action list above loc
            self.dispObj.clearActionTrnRecs(loc, trainNam)
    
class routeMgmt():
    
    def __init__(self):
        self.rtCapsObj = rtCaps()
        pass
                
    def addTrn2Route(self, routeNam, trainNam):
        routeStem = routeCls.routes[routeNam]["trains"]
        if trainNam in routeStem: return
        routeStem.append(trainNam)
        dir = trainDB.trains[trainNam]["direction"]
        if dir == "east":
            rtCaps.rtCap[routeNam]["nEastTns"] +=1
        elif dir == "west":
            rtCaps.rtCap[routeNam]["nWestTns"] +=1
       
    def remTrnsOnRoute(self, routeNam, trainNam):
        routeStem = routeCls.routes[routeNam]["trains"]
        try:
            index = routeStem.index(trainNam)
            routeStem.pop(index)
        except:
            pass
        
        self.rtCapsObj.remTrnFrmRouteQ(routeNam, trainNam)
        dir = trainDB.trains[trainNam]["direction"]
        numEast = rtCaps.rtCap[routeNam]["nEastTns"]
        numWest = rtCaps.rtCap[routeNam]["nWestTns"]
        if dir == "east":
            num = max(numEast -1, 0)
            rtCaps.rtCap[routeNam]["nEastTns"] = num
        elif dir == "west":
            num = max(numWest -1, 0)
            rtCaps.rtCap[routeNam]["nWestTns"] = num
        
    def trnArrivalTimes(self):
        for routeNam in routeCls.routes:
            routeStem = routeCls.routes[routeNam]
            for trainNam in routeStem["trains"]:
                self.calcTrnArrTime("trnArrTimes:route ", routeNam, trainNam)
            for trainNam in rtCaps.rtCap[routeNam]["Q"]:
                self.calcTrnArrTime("trnArrTimes:loc ", routeNam, trainNam)

    def calcTrnArrTime(self, callFunc, loc, trainNam):
        print("calcTrnArrTime; called from: ", callFunc, " loc: ", loc, " , trainNam: ", trainNam)
        trainStem = trainDB.trains[trainNam]
        if "route" in loc:
            routeStem = routeCls.routes[loc]
            dist2Go = routeStem["rtLength"] - \
                trainStem["coord"]["xRoute"]
        else:
            rtToEnter = trainStem["rtToEnter"]
            routeStem = routeCls.routes[rtToEnter]
            dist2Go = routeCls.routes[rtToEnter]["rtLength"]
        time2Go = abs(dist2Go)/routeStem["distPerTime"]
        trainStem["estArrTime"] = round(mVars.time + time2Go, 2)
                
#=================================================
class rtCaps():
    rtCap = {}
    
    def __init__(self):
        pass
    
    def initRouteCaps(self):
        rtCaps.rtCap = files.readFile("routeCapFile")
        for route in rtCaps.rtCap:
                   
            pass
    
    def printRtCaps(self):
        print("\nrtCaps.rtCap: ")
        for route in rtCaps.rtCap:
            print(route, ":", "trains on route:", 
                  routeCls.routes[route]["trains"],
                  rtCaps.rtCap[route])
            
    def updateRtSlots(self):
        for route in rtCaps.rtCap:
            # trains already on the route
            rtStem = rtCaps.rtCap[route]
            eastSlots = 0
            westSlots = 0
            numEast = rtStem["nEastTns"]
            numWest = rtStem["nWestTns"]
            if numEast == 0 and numWest == 0:
                eastSlots = max(rtStem["samNoOpoCap"], 0)
                westSlots = eastSlots
            elif numEast != 0 and numWest == 0:
                eastSlots = max(rtStem["samNoOpoCap"] - numEast, 0)
                westSlots = max(rtStem["oppoDirCap"] - numWest, 0)
            elif numEast == 0 and numWest != 0:
                westSlots = max(rtStem["samNoOpoCap"] - numWest, 0)
                eastSlots = max(rtStem["oppoDirCap"] - numEast, 0)
            elif numEast != 0 and numWest != 0:
                if (numEast < rtStem["samOppoCap"]) and \
                    (numWest <= rtStem["oppoDirCap"]):
                    eastSlots = max(rtStem["samOppoCap"] - numEast, 0)
                    westSlots = max(rtStem["oppoDirCap"] - numWest, 0)
                elif (numWest < rtStem["samOppoCap"]) and \
                    (numEast <= rtStem["oppoDirCap"]):
                    westSlots = max(rtStem["samOppoCap"] - numWest, 0)
                    eastSlots = max(rtStem["oppoDirCap"] - numEast, 0)

            rtStem["eastSlots"] = eastSlots
            rtStem["westSlots"] = westSlots                    

    def addTrn2RouteQ(self, route, trainNam):
        if trainNam not in rtCaps.rtCap[route]["Q"]:
            rtCaps.rtCap[route]["Q"].append(trainNam)

    def remTrnFrmRouteQ(self, route, trainNam):
        rtCapStem = rtCaps.rtCap[route]["Q"]
        try:
            index = rtCapStem.index(trainNam)
            rtCapStem.pop(index)
        except:
            pass

    def checkRtSlots(self, trainNam):
        #look at train's requested dir, route
        # if slot available, and arrival track
        # available, put on route
        openSlot = False
        trainStem = trainDB.trains[trainNam]
        routeNam = trainStem["rtToEnter"]
        rtStem = rtCaps.rtCap[routeNam]
        dir = trainStem["direction"]
        if dir == "east":
            if rtStem["eastSlots"] >0:
                rtStem["eastSlots"] -=1
                openSlot = True
            else: openSlot = False
        elif dir == "west":
            if rtStem["westSlots"] >0:
                rtStem["westSlots"] -=1
                openSlot = True
            else: openSlot = False
                
        return openSlot
        

