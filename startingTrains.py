
from fileProc import readFiles
files = readFiles()
from stateVars import trainDB, locs, routeCls

class startingTrains():
    
    def __init__(self):
        pass
    
    def dict2TrnNam(self, train):
        self.trnName = next(iter(train))
    def dict2ConNam(self, consist):
        self.conName = next(iter(consist))

    def initTrain(self):
        
        self.train = files.readFile("trainFile")
        self.dict2TrnNam(self.train)
        self.train[self.trnName]["color"] = trainDB.colors()
        print("color for init train: ", self.train[self.trnName]["color"])

        print("adding initial consist")
        self.initConsist(files, "consistFile")
        self.conName
        tmpLoc = self.train[self.trnName]["currentLoc"]
        if "route" in tmpLoc:
            mVars.routes[tmpLoc]["trains"].append(self.trnName)
        self.consist[self.conName]["trainNum"] = self.train[self.trnName]["trainNum"]
        trainDB.consists.update(self.consist)
        self.train[self.trnName]["consistNum"] = self.consist[self.conName]["consistNum"]
        trainDB.trains.update(self.train)
        return 

    def initConsist(self, files, fkey):
        self.consist = files.readFile(fkey)
        self.conNam(self.consist)
        print("\ncreating consist ", self.conName)
        self.consist[self.conName]["consistNum"] = trainDB.numConsists
        trainDB.numConsists +=1
        if mVars.prms["dbgTrnInit"]: print("consistDict: ", self.consist)
        return
