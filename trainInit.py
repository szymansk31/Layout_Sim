
from mainVars import mVars
from fileProc import readFiles
from display import dispItems
from locProc import locProc, locBase
from coords import transForms
from stateVars import locs, dspCh, trainDB, routeCls


#=================================================
class trainInit():
    trnHeight = 10
    trnLength = 20
    colorIDX = 0
    colorList = ["red", "green", "yellow", "orange", "purple1", "dodger blue", "deep pink",
                 "lawn green", "goldenrod", "OrangeRed2", "magenta2", "RoyalBlue1"]
    trnStatusList = ["enroute", "ready2Leave", "init", "building", "built", "terminate", "rdCrwSw",
                     "dropPickup", "continue", "turn", "misc", "stop"]


    def __init__(self):
        #self.trainID = int
        self.trainNam = ""
        self.conName = ""
        self.files = readFiles()

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
            
    def newTrain(self, newTrainNam):
        newTrain = {}
        #newTrainNum = trainDB.numTrains+1
        newTrainNum = newTrainNam[5:]
        #newTrainNam = "train"+str(newTrainNum)
        newConsistNum = trainDB.numConsists+1 
        newConsistNam = "consist"+str(newConsistNum)
        tmpTrain = self.files.readFile("trainFile")
        
        newTrain[newTrainNam] = tmpTrain.pop("trnProtype")
        newTrain[newTrainNam]["trainNum"] = newTrainNum
        newTrain[newTrainNam]["consistNum"] = newConsistNum
        newTrain[newTrainNam]["numCars"] = 0
    
        print("newTrain: partial dict: ", newTrain)
        trainDB.trains.update(newTrain)
        
        self.newConsist(newConsistNum, newTrainNum)
        trainDB.numTrains +=1
        trainDB.numConsists +=1
        return newConsistNam
    
    def initNewTrain(self, loc, newTrainNam):
        conName = self.newTrain(newTrainNam)
        
        #nextLoc, numstops, stops = self.setStops(loc, maxCarTrk)
        stops = trainDB.trains[newTrainNam]["stops"]
        numStops = 0
        for stopLoc in stops:
            numStops += 1 
        nextLoc = next(iter(stops))
        print("train: ", newTrainNam, ", stops: ", stops)
        trainDB.trains[newTrainNam].update( {
            "status": "building",
            "origLoc": loc,
            "nextLoc": nextLoc,
            "currentLoc": loc,
            "finalLoc": stopLoc,
            "numStops": numStops,
            "departStop": loc,
            "stops": stops,
            "color": trainInit.colors()           
                })
        # consist gets stops that have cars to drop, not those where
        # the train continues through.  Pickups are triggered by
        # "dropPickup" status in that location and will add to consists
        tmpDict = {}
        for conStop in stops:
            tmpDict.update({conStop: {"box": 0, "tank": 0,"rfr": 0, "hop": 0, 
            "gons": 0, "flats": 0}})
        trainDB.consists[conName].update({
            "stops": tmpDict
        })
        
        print("new train: ", newTrainNam, ": ", trainDB.trains[newTrainNam])
        print("new consist: ", conName, ":", trainDB.consists[conName])
        #trainDB.ydTrains["buildTrain"].append(newTrainNam)
        return

    def fillTrnDicts(self, loc, trainNam):
        
        numStops, stops, lastStop = self.calcStops(trainNam)
        nextLoc = next(iter(stops))
        print("train: ", trainNam, ", stops: ", stops)
        currentLoc = loc if loc != "unknown" else loc
        trainDB.trains[trainNam].update( {
            "status": "building",
         #sched files need to have these two locs set right
        #    "origLoc": origLoc,  
        #    "currentLoc": loc,
            "departStop": loc,  # by def'n the loc
            "nextLoc": nextLoc,
            "finalLoc": lastStop,
            "numStops": numStops,
            "stops": stops,
            "color": trainInit.colors()           
                })
        
        conNam = self.calcConsist(stops, trainNam)
        print("new train: ", trainNam, ": ", trainDB.trains[trainNam])
        print("new consist: ", conNam, ":", trainDB.consists[conNam])
        trainDB.numTrains +=1

        return

    def calcStops(self, trainNam):
        #stops are given in sched files
        stops = trainDB.trains[trainNam]["stops"]
        numStops = 0
        if stops != None:
            for stopLoc in stops:
                numStops += 1 

            return numStops, stops, stopLoc   
        else:
            numStops, stops = self.setStops(loc, dest)  
        #calculate stops   

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
                # provided in sched file
                tmpDict = {}
                for consistStop in stops:
                    tmpDict.update({consistStop: {"box": 0, "tank": 0,"rfr": 0, "hop": 0, 
                    "gons": 0, "flats": 0}})
                trainDB.consists[conNam].update({
                    "stops": tmpDict
                })
            trainDB.numConsists +=1
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

    def setStops(self, loc, dest):
        from gui import gui
        stops = {}
        testLoc = loc
        nextLoc = dest
        numStops = 0
        while 1:
            if dest in locs.locDat[testLoc]["adjLocNames"].values():
                stops.update({dest: {"action": "terminate"}})
                numStops +=1
                return nextLoc, numStops, stops

            if gui.guiDict[dest]["x0"] < gui.guiDict[loc]["x0"]:
                tmpStop = locs.locDat[testLoc]["adjLocNames"]["W"]
                stops[tmpStop] = dict(action = "continue")
                numStops +=1
            else:
                tmpStop = locs.locDat[testLoc]["adjLocNames"]["E"]
                stops[tmpStop] = dict(action = "continue")
                numStops +=1
            if numStops == 1: nextLoc = tmpStop
            testLoc = tmpStop    
        
        return
