
from fileProc import readFiles
from stateVars import trainDB, locs, routeCls
from mainVars import mVars
from trainProc import trainParams

files = readFiles()

class trainFromFile():
    
    def __init__(self):
        pass
    
    def dict2TrnNam(self, train):
        self.trnName = next(iter(train))
    def dict2ConNam(self, consist):
        self.conName = next(iter(consist))

    def readTrain(self):
        
        trainDict = files.readFile("startingTrainFile")
        for train in trainDict:
            trainDict[train]["color"] = trainParams.colors()
            print("color for init train: ", trainDict[train]["color"])

            print("adding initial consist")
            self.consistFromFile(files, "startingConsistFile")
            self.dict2ConNam
            trainDict[train]["trnObjTag"] = train+"ObjTag"
            trainDict[train]["trnLabelTag"] = train+"LabelTag"

            tmpLoc = trainDict[train]["currentLoc"]
            if "route" in tmpLoc:
                routeCls.routes[tmpLoc]["trains"].append(train)
            self.consist[self.conName]["trainNum"] = trainDict[train]["trainNum"]
            trainDB.consists.update(self.consist)
            trainDict[train]["consistNum"] = self.consist[self.conName]["consistNum"]
            newTrain = {}
            newTrain[train] = trainDict[train]

            print("newTain dict in startingTrains: ", newTrain)
            trainDB.trains.update(newTrain)
            print("starting train: ", trainDB.trains[train])
        return 

    def consistFromFile(self, files, fkey):
        self.consist = files.readFile(fkey)
        self.dict2ConNam(self.consist)
        print("\ncreating consist ", self.conName)
        if mVars.prms["dbgTrnInit"]: print("consistDict: ", self.consist)
        return
