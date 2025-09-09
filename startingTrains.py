
from fileProc import readFiles
from stateVars import trainDB, locs, routeCls
from mainVars import mVars
from trainInit import trainInit
from display import dispItems
from gui import gui
from coords import transForms
from locProc import locProc
from locBase import locBase
from routeProc import rtCaps

files = readFiles()

class trainFromFile():
    
    def __init__(self):
        pass
    
    def dict2TrnNam(self, trainNam):
        self.trnName = next(iter(trainNam))
    def dict2ConNam(self, consist):
        self.conName = next(iter(consist))
        
    def readTrain(self):
        trainInitObj = trainInit()
        locProcObj = locProc()
        trainDict = files.readFile("startingTrainFile")
        self.consistFromFile(files, "startingConsistFile")
        trainDB.consists.update(self.consist)
        for trainNam in trainDict:
            print("\nTrain: ", trainNam)
            trainDB.strtTrns.append(trainNam)
            currLoc = trainDict[trainNam]["currentLoc"]

            trainDict[trainNam]["color"] = trainInit.colors()
            #print("color for init train: ", trainDict[train]["color"])

            print("adding initial consist")
            trainDict[trainNam]["trnRectTag"] = trainNam+"RectTag"
            trainDict[trainNam]["trnNumTag"] = trainNam+"NumTag"
            trainDict[trainNam]["trnLabelTag"] = trainNam+"LabelTag"
            consistNum = trainDict[trainNam]["consistNum"]
            consistNam = "consist"+str(consistNum)

            #self.consist[self.conName]["trainNum"] = trainDict[train]["trainNum"]
            #trainDict[train]["consistNum"] = self.consist[self.conName]["consistNum"]
            newTrain = {}
            newTrain[trainNam] = trainDict[trainNam]

            print("newTain dict in startingTrains: ", newTrain)
            print("with consist: ", consistNam, ", contents: ", self.consist[consistNam])
            trainDB.trains.update(newTrain)
            trainDB.trains[trainNam]["numCars"] = trainInitObj.numCars(trainNam)
            origLoc = trainDict[trainNam]["origLoc"]
            locProcObj.startTrain(origLoc, trainNam)
            print("starting train: ", trainDB.trains[trainNam])
            dispObj = dispItems()
            dispObj.drawTrain(trainNam)
        return 

    def consistFromFile(self, files, fkey):
        self.consist = files.readFile(fkey)
        self.dict2ConNam(self.consist)
        print("\ncreating consist ", self.conName)
        #if mVars.prms["dbgTrnInit"]: print("consistDict: ", self.consist)
        return
