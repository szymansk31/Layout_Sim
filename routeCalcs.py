import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from coords import transForms
from fileProc import readFiles
files = readFiles()

np.set_printoptions(precision=2, suppress=True) 

class routeInit():
    
    def __init__(self):
        pass
    
class routeMgmt():
    
    def __init__(self):
        pass
    
    def fillTrnsOnRoute(self, routeNam, trainNam):
        routeStem = routeCls.routes[routeNam]["trains"]
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
        
        dir = trainDB.trains[trainNam]["direction"]
        numEast = rtCaps.rtCap[routeNam]["nEastTns"]
        numWest = rtCaps.rtCap[routeNam]["nWestTns"]
        if dir == "east":
            num = max(numEast -1, 0)
            rtCaps.rtCap[routeNam]["nEastTns"] = num
        elif dir == "west":
            num = max(numWest -1, 0)
            rtCaps.rtCap[routeNam]["nWestTns"] = num
        
    def calcTrnArrivalTime(self, route):
        for route in routeCls.routes:
            routeStem = routeCls.routes[route]
            for train in routeStem["trains"]:
                trainStem = trainDB.trains[train]
                dist2Go = routeStem["rtLength"] - \
                    trainStem["coord"]["xRoute"]
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
        

