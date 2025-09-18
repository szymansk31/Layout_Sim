
from fileProc import readFiles
from stateVars import locs, dspCh, trainDB, routeCls

#=================================================
class trainInit():
    trnHeight = 10
    trnLength = 20
    colorIDX = 0
    colorList = ["red", "green", "yellow", "orange", "purple1", "dodger blue", "deep pink",
                 "lawn green", "goldenrod", "OrangeRed2", "magenta2", "RoyalBlue1"]
    trnStatusList = ["enroute", "wait4Clrnce", "waitOnRoute", "init", "building", "built", 
                     "terminate", "rdCrwSw",
                     "dropPickup", "continue", "turn", "misc", "stop"]


    def __init__(self):
        #self.trainID = int
        self.trainNam = ""
        self.conName = ""
        self.files = readFiles()
        from locBase import locMgmt
        self.locMgmtObj = locMgmt()
        from routeProc import routeMgmt
        self.rtMgmtObj = routeMgmt()
        pass
    
    @classmethod
    def colors(cls):
        maxColorIDX = 12
        cls.color = cls.colorList[cls.colorIDX]
        cls.colorIDX +=1
        if cls.colorIDX == maxColorIDX: cls.colorIDX = 0
        print("color: ", cls.color)
        return cls.color
        

    def dict2TrnNam(self, train):
        self.trainNam = next(iter(train))
    def dict2ConNam(self, consist):
        self.conName = next(iter(consist))
    def addTrn2TrainDB(trainDict):
        trainDB.trains.update(trainDict)

    def numCars(self, train):
        consistNam = trainDB.getConNam(train)
        consist = trainDB.consists[consistNam]
        numCars = 0
        for loc in consist["stops"]:
            numCars += sum(consist["stops"][loc].values())
        return numCars
            
    def fillTrnDicts(self, loc, trainNam):
        
        finalLoc = trainDB.trains[trainNam]["finalLoc"]
        numStops, stops, nextLoc = self.calcStops(loc, finalLoc, trainNam)
        print("train: ", trainNam, ", stops: ", stops)
        conNam = self.calcConsist(stops, trainNam)
        numCars = self.numCars(trainNam)
        self.addTags(trainNam)
        trainDB.trains[trainNam].update( {
            "trainNum": trainNam[5:],
            "consistNum": conNam[7:],
            "numCars": numCars,
        #    "status": "building",
         #sched files need to have these three locs set right
        #    "origLoc": origLoc,  
        #    "currentLoc": loc,
        #    "finalLoc": lastStop,
            "departStop": loc,  # by def'n the loc
            "nextLoc": nextLoc,
            "numStops": numStops,
            "stops": stops,
            "color": trainInit.colors()           
                })
        
        self.locMgmtObj.findRtPrms(loc, trainNam)
        self.rtMgmtObj.calcTrnArrTime("fillTrnDicts ", loc, trainNam)
        print("new train: ", trainNam, ": ", trainDB.trains[trainNam])
        print("new consist: ", conNam, ":", trainDB.consists[conNam])

        return

    def calcStops(self, loc, finalLoc, trainNam):
        #stops defined in sched files, but may be blank
        stops = trainDB.trains[trainNam]["stops"]
        numStops = 0
        if stops != {}:
            for stopLoc in stops:
                numStops += 1 
            nextLoc = next(iter(stops))
        else:
            numStops, stops, nextLoc = self.findStops(loc, finalLoc)  
        return numStops, stops, nextLoc   

    def calcConsist(self, stops, trainNam):
        # consist gets stops that have cars to drop, not those where
        # the train continues through.  Pickups are triggered by
        # "dropPickup" status in that location and will add to consists
         
        if trainDB.trains[trainNam]["consistNum"] == 0:
            newConsistNum = trainDB.numConsists+1 
            conNam = "consist"+str(newConsistNum) 
            self.newConsist(newConsistNum, trainNam[5:])
            if stops == None:
                # no information about stops from sched
                # files; use new blank consist created above
                pass
            else:
                # consist can be calculated from stops
                # provided in sched file and updated in trainDB.consists
                tmpDict = {}
                for consistStop in stops:
                    tmpDict.update({consistStop: {"box": 0, "tank": 0,"rfr": 0, "hop": 0, 
                    "gons": 0, "flats": 0}})
                trainDB.consists[conNam].update({
                    "stops": tmpDict
                })
            trainDB.numConsists +=1
            trainDB.trains[trainNam]["consistNum"] = newConsistNum
        else:
            consistNum = trainDB.trains[trainNam]["consistNum"]
            conNam = "consist"+str(consistNum)

        return conNam
    
    def newConsist(self, newConsistNum, newTrainNum):
        newConNam = "consist"+str(newConsistNum)
        trainDB.consists.update(
        {
        newConNam: {
            "consistNum": newConsistNum,
            "trainNum": newTrainNum,
            "stops": {
                "yard"   :{"box": 0, "tank": 0,"rfr": 0, "hop": 0, 
                    "gons": 0, "flats": 0},
                }
            }
        })
        return 

    def addTags(self, trainNam):
        trainStem = trainDB.trains[trainNam]
        trainStem["trnRectTag"] = trainNam+"RectTag"
        trainStem["trnNumTag"] = trainNam+"NumTag"
        trainStem["trnLabelTag"] = trainNam+"LabelTag"

    def findStops(self, loc, dest):
        adjLocWest = locs.locDat[loc]["adjLocWest"]
        adjLocEast = locs.locDat[loc]["adjLocEast"]
        print("findStops; loc:", loc, ", dest:", dest)
        print("adjLocWest:", adjLocWest,
              ", adjLocEast:", adjLocEast)
        from gui import gui
        stops = {}
        currLoc = loc
        nextLoc = dest
        nWestAdjLocs = len(adjLocWest)
        nEastAdjLocs = len(adjLocEast)
        eastLocIdx = 0
        westLocIdx = 0
        numStops = 0
        if gui.guiDict[nextLoc]["x0"] < gui.guiDict[currLoc]["x0"]:
            searchDir = "west"
        else: searchDir = "east"
        while 1:
            match searchDir:
                case "west":
                    locList = locs.locDat[currLoc]["adjLocWest"]
                case "east":
                    locList = locs.locDat[currLoc]["adjLocEast"]
            if dest in locList:
                stops.update({dest: {"action": "terminate"}})
                numStops +=1
                return numStops, stops, nextLoc

                if searchDir == "west" and westLocIdx == nWestAdjLocs: westLocIdx +=1
                if searchDir == "east" and eastLocIdx == nEastAdjLocs: eastLocIdx +=1
                eastLocIdx +=1
                

            if searchDir == "west":
                tmpStop = locs.locDat[currLoc]["adjLocWest"][westLocIdx]
            else:
                tmpStop = locs.locDat[currLoc]["adjLocEast"][eastLocIdx]
            stops[tmpStop] = dict(action = "continue")
            currLoc = tmpStop
            numStops +=1
            if numStops == 1: nextLoc = tmpStop
                
        
        return
    
    def chooseBranchLine(self, loc, dest):
        pass
