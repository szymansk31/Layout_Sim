
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
        
        self.train = files.readFile("startingTrainFile")
        self.dict2TrnNam(self.train)
        self.train[self.trnName]["color"] = trainParams.colors()
        print("color for init train: ", self.train[self.trnName]["color"])

        print("adding initial consist")
        self.consistFromFile(files, "startingConsistFile")
        self.dict2ConNam
        self.train[self.trnName]["trnObjTag"] = self.trnName+"ObjTag"
        self.train[self.trnName]["trnLabelTag"] = self.trnName+"LabelTag"

        tmpLoc = self.train[self.trnName]["currentLoc"]
        if "route" in tmpLoc:
            routeCls.routes[tmpLoc]["trains"].append(self.trnName)
        self.consist[self.conName]["trainNum"] = self.train[self.trnName]["trainNum"]
        trainDB.consists.update(self.consist)
        self.train[self.trnName]["consistNum"] = self.consist[self.conName]["consistNum"]
        trainDB.trains.update(self.train)
        print("starting train: ", trainDB.trains[self.trnName])
        return 

    def consistFromFile(self, files, fkey):
        self.consist = files.readFile(fkey)
        self.dict2ConNam(self.consist)
        print("\ncreating consist ", self.conName)
        if mVars.prms["dbgTrnInit"]: print("consistDict: ", self.consist)
        return
