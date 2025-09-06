import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from display import dispItems
from coords import transForms
        
np.set_printoptions(precision=2, suppress=True) 

dbgLocal = 1     
#=================================================
class locBase():
    
    def __init__(self):
        from routeProc import routeMgmt, rtCaps
        self.routeMgmtObj = routeMgmt()
        pass
    
    def initLocDicts(self):
        from fileProc import readFiles
        files = readFiles()
        print("initializing location dicts: ")
        locs.locDat = files.readFile("locationFile")
        for loc in locs.locDat:
            self.countCars(loc)
            locs.locDat[loc]["locTrnRectID"] = loc+"TrnRectID"
            locs.locDat[loc]["locTrnNumID"] = loc+"TrnNumID"
            locs.locDat[loc]["locRectID"] = loc+"RectID"
            
        QmgmtObj = Qmgmt()
        QmgmtObj.initLocQs()
        QmgmtObj.initLocArrDepSlots()
        
    def countCars(self, loc):
        locStem = locs.locDat[loc]
        type = locs.locDat[loc]["type"]
        locStem["totCars"] = 0
        match type:
            case "yard":
                trackStem = locStem["tracks"]
            case "swArea":
                trackStem = locStem["industries"]
        if type == "staging":
            for train in locStem["trains"]:
                locStem["totCars"] += trainDB.trains[train]["numCars"]
            return
        for trackNam in locStem["destTrkTots"]:
            #print("\n Location: ", loc, "destination: ", trackNam)
            if trackNam not in trackStem: continue
            match type:
                case "yard":
                    locStem["destTrkTots"][trackNam] = sum(trackStem[trackNam].values())
                    locStem["totCars"] += locStem["destTrkTots"][trackNam]
                case "swArea":
                    if trackNam == "offspot": 
                        locStem["numOffspot"] = sum(locs.locDat[loc]["offspot"].values())
                        continue
                    locStem["indusTots"][trackNam] = \
                        sum(trackStem[trackNam]["pickups"].values()) + \
                        sum(trackStem[trackNam]["leave"].values())
                    locStem["totCars"] += locStem["indusTots"][trackNam]
                    locStem["totCars"] += locStem["numOffspot"]
                                            

    def locDests(self, loc):
        thisLocDests = []
        for dest in locs.locDat[loc]["destTrkTots"]:
            thisLocDests.append(dest)
        return thisLocDests
    
#=================================================
class Qmgmt():
    
    def __init__(self):
        from routeProc import routeMgmt, rtCaps
        self.routeMgmtObj = routeMgmt()
        pass
    
    def initLocQs(self):
        # remove placeholder/prototype of each Q from input files
        for loc in locs.locDat:
            QStem = locs.locDat[loc]["Qs"]
            for Q in QStem:
                QStem[Q].pop(0)
    
    def initLocArrDepSlots(self):
        for loc in locs.locDat:
            locStem = locs.locDat[loc]
            for track in locStem["trkPrms"]:
                if "arrival" in locStem["trkPrms"][track]["funcs"]:
                    locStem["trkCounts"]["numArrTrks"] += 1
                if "depart" in locStem["trkPrms"][track]["funcs"]:
                    locStem["trkCounts"]["numDepTrks"] += 1
                if ("arrival" in locStem["trkPrms"][track]["funcs"]) and \
                (locStem["trkPrms"][track]["status"] == "unAssnd"):
                    locStem["trkCounts"]["openArrTrks"] += 1

                    
    def calcDeptTimes(self):
        for loc in locs.locDat:
            locStem = locs.locDat[loc]
            for trainNam in locStem["trains"]:
                estDeptTime = mVars.time + trainDB.avgSwTime
                trainDB.trains[trainNam]["estDeptTime"] = round(estDeptTime, 2)
        #calc estDeptTime for all trains enroute; calc above is
        # for trains in locations being worked.  Unlike arrTime calcs
        # trains in route Qs are still formally in a loc and caught above
        for route in routeCls.routes:
            for trainNam in routeCls.routes[route]["trains"]:
                estArrTime = trainDB.trains[trainNam]["estArrTime"]
                trainDB.trains[trainNam]["estDeptTime"] = round(estArrTime + trainDB.avgSwTime, 2)
        pass
                
    def calcArrivTrns(self):
        self.routeMgmtObj.trnArrivalTimes()
        for route in routeCls.routes:
            for trainNam in routeCls.routes[route]["trains"]:
                estArrTime = trainDB.trains[trainNam]["estArrTime"]
                loc = trainDB.trains[trainNam]["nextLoc"]
                #if estArrTime - mVars.time <= mVars.prms["arrTimDelta"]:
                self.addTrn2LocQ(loc, "arrivals", trainNam, "")
                
    def sortLocQ(self, QNam, sortVar):
        def getTimVal(subDict):
            for key, value in subDict.items():
                return value[sortVar]
        for loc in locs.locDat:
            tmpList = locs.locDat[loc]["Qs"][QNam]
            locs.locDat[loc]["Qs"][QNam] = sorted(tmpList, key=getTimVal)
            print("loc: ", loc, " , Q: ", QNam, locs.locDat[loc]["Qs"][QNam])   
            
    # track is an optional input if known           
    def addTrn2LocQ(self, loc, QNam, trainNam, track):
        if any(trainNam in d for d in locs.locDat[loc]["Qs"][QNam]): return
        conNam = trainDB.getConNam(trainNam)
        trainStem = trainDB.trains[trainNam]
        
        match QNam:
            case "arrivals":
                nCars4ThisLoc = sum(trainDB.consists[conNam]["stops"][loc].values())
                locs.locDat[loc]["Qs"]["arrivals"].append({ \
                    trainNam: {"estArrTime": trainStem["estArrTime"],
                    "action": trainStem["stops"][loc]["action"],
                    "arrTrk": track,
                    "nCars4ThisLoc": nCars4ThisLoc,
                    "estDeptTime": trainStem["estDeptTime"]}})
            case "working":
                locs.locDat[loc]["Qs"]["working"].append({ \
                    trainNam: {"estDeptTime": trainStem["estDeptTime"],
                    "status": trainStem["status"],
                    "rtToEnter": trainStem["rtToEnter"]}})
            case "builds":
                numCars2Add = mVars.prms["trainSize"] - trainStem["numCars"]
                locs.locDat[loc]["Qs"]["builds"].append({ \
                    trainNam: {"numCars": trainStem["numCars"],
                    "numCars2Add": numCars2Add,
                    "status": trainStem["status"],
                    "rtToEnter": trainStem["rtToEnter"]}})

    def remTrnLocQ(self, loc, QNam, trainNam):
        QStem = locs.locDat[loc]["Qs"][QNam]
        index = [idx for idx, d in enumerate(QStem) if trainNam in d]
        try:
            QStem.pop(index[0])
        except:
            return
        
    def updateArrvQs(self):
        for loc in locs.locDat:
            QStem = locs.locDat[loc]["Qs"]["arrivals"]
            for QDict in QStem:
                trainNam = next(iter(QDict))
                self.updateLocQ(loc, "arrivals", trainNam)

    def updateLocQ(self, loc, QNam, trainNam):
        if not any(trainNam in d for d in locs.locDat[loc]["Qs"][QNam]): return
        conNam = trainDB.getConNam(trainNam)
        trainStem = trainDB.trains[trainNam]
        
        match QNam:
            case "arrivals":
                QStem = locs.locDat[loc]["Qs"]["arrivals"]
                #nCars4ThisLoc = sum(trainDB.consists[conNam]["stops"][loc].values())
                index = [idx for idx, d in enumerate(QStem) if trainNam in d]
                locs.locDat[loc]["Qs"]["arrivals"][index[0]][trainNam].update({ \
                    "estArrTime": trainStem["estArrTime"],
                    #"action": trainStem["stops"][loc]["action"],
                    #"arrTrk": trainStem["arrTrk"],
                    #"nCars4ThisLoc": nCars4ThisLoc,
                    "estDeptTime": trainStem["estDeptTime"]})

    def readArrTrk(self, loc, trainNam):
        QStem = locs.locDat[loc]["Qs"]["arrivals"]
        index = [idx for idx, d in enumerate(QStem) if trainNam in d]
        try:
            arrTrk = QStem[index[0]][trainNam]["arrTrk"]        
            return arrTrk
        except:
            return ""
    
    def setArrTrk(self, loc, trainNam, arrTrk):
        QStem = locs.locDat[loc]["Qs"]["arrivals"]
        index = [idx for idx, d in enumerate(QStem) if trainNam in d]
        QStem[index[0]][trainNam]["arrTrk"] = arrTrk
        
    def remTrnArrTrk(self, loc, track, trainNam):
        print("removing train ", trainNam, " from arr track: ", track, "in loc ", loc)
        try:
            locStem = locs.locDat[loc]["trkPrms"]
            locStem[track]["train"] = ""
            locStem[track]["status"] = "unAssnd"
            locs.locDat[loc]["trkCounts"]["openArrTrks"] +=1
            return
        except:
            return
    
                                
#=================================================
class locMgmt():
    
    def __init__(self):
        from routeProc import routeMgmt, rtCaps
        self.rtCapsObj = rtCaps()
        self.rtMgmtObj = routeMgmt()
        self.QmgmtObj = Qmgmt()
        pass
                   
    def rmTrnFrmActions(self, action, loc, trainNam):
        dispObj = dispItems()
        # remove train from ydTrains and location
        print("rmTrnFrmActions: trainDB.ydTrains: ", trainDB.ydTrains)
        try:
            index = trainDB.ydTrains[action].index(trainNam)
            trainDB.ydTrains[action].pop(index)
        except:
            pass
        if dbgLocal: print("after removal: trainDB.ydTrains: ", trainDB.ydTrains)

        # clear action data from display
        dispObj.clearActionDat(loc)
    
    def rmTrnFrmLoc(self, loc, trainNam):  
        try:
            index = locs.locDat[loc]["trains"].index(trainNam)
            locs.locDat[loc]["trains"].pop(index)
        except:
            print("cannot remove train ", trainNam, " from loc ", loc)
            pass
        

    def placeTrain(self, loc, trainStem, trainNam): 
        coordObj = transForms()
        #if trainStem["status"] == "init":
        #    loc = trainStem["rtToEnter"]
        if "route" in loc:
            self.setTrnCoord(loc, trainNam)
            # fill trainDB with xPlot and yPlot, the canvas/screen coords
            coordObj.xRoute2xPlot(loc, trainNam)
            self.rtCapsObj.addTrn2RouteQ(loc, trainNam)
            #self.rtMgmtObj.addTrn2Route(loc, trainNam)
            self.QmgmtObj.addTrn2LocQ(trainStem["nextLoc"], "arrivals", trainNam, "")
            return
        else:
            locs.locDat[loc]["trains"].append(trainNam)
            self.QmgmtObj.updateLocQ(loc, "arrivals", trainNam)
            return

    def setTrnCoord(self, currLoc, trainNam):
        routeLen = routeCls.routes[currLoc]["rtLength"]
        trainStem = trainDB.trains[trainNam]
        trainStem["coord"]["yRoute"] = 0 # by definition rotated coord system is
            # along xRoute axis
        xRoute = trainStem["coord"]["xTrnInit"]*routeLen
        if trainStem["direction"] == "west":
                xRoute = -xRoute
        trainStem["coord"]["xRoute"] = xRoute    
        return 

        
    def findRoutes(self, loc, trainNam):
        nextLoc = trainDB.trains[trainNam]["nextLoc"]
        for routeNam in routeCls.routes:
            loc = ''.join(loc)
            dest = ''.join(nextLoc)
            if dbgLocal: print("routNam: ", routeNam, " loc: ", loc, 
                " nextLoc: ", dest, "route: ", routeCls.routes[routeNam])
            if (loc in routeCls.routes[routeNam].values()) and \
                (dest in routeCls.routes[routeNam].values()):
                return routeNam
        
    def findRtPrms(self, loc, trainNam):
        # setup train
        trainStem = trainDB.trains[trainNam]
        dest = trainDB.trains[trainNam]["nextLoc"]
        if dest != "":
            # setup new route
            route4newTrn = self.findRoutes(loc, trainNam)
            trainStem["rtToEnter"] = route4newTrn
            westObj = routeCls.routes[route4newTrn]["westObj"].strip()
            eastObj = routeCls.routes[route4newTrn]["eastObj"].strip()
            #routeCls.routes[route4newTrn]["trains"].append( trainNam)
            if loc == westObj: 
                trainStem["direction"] = "east"
            elif loc == eastObj:
                trainStem["direction"] = "west"
            else: 
                print("no route found",  trainNam,  "westObj: ", westObj, "eastObj: "
                        , eastObj,"loc: ", loc, "direction: ", trainStem["direction"])
                trainStem["status"] = "stop"
        return 
                    

    def cleanupSwAction(self, loc, trainNam, action):
        dispObj = dispItems()
        locActionStem = locs.locDat[loc]["trn4Action"]            
        index = [i for i, d in enumerate(locActionStem)\
            if action in d]
        if index:
            locActionStem.pop(index[0])
        try:
            trainStem = trainDB.trains[trainNam]
            # remove stop from train
            trainStem["stops"].pop(loc)
            # remove stop from consist
            consistNam = trainDB.getConNam(trainNam)
            trainDB.consists[consistNam]["stops"].pop(loc)
        except:
            pass
        # remove from ydTrains action list
        self.rmTrnFrmActions(action, loc, trainNam)

        # clear action data from display
        dispObj.clearActionDat(loc)

    
