#unused code:
def initTrain(self):
    self.train = self.files.readFile("trainFile")
    self.dict2TrnNam(self.train)
    self.train[self.trnName]["color"] = trainDB.colors()
    print("color for init train: ", self.train[self.trnName]["color"])

    print("adding initial consist")
    self.initConsist("consistFile")
    self.conName
    tmpLoc = self.train[self.trnName]["currentLoc"]
    if "route" in tmpLoc:
        routeCls.routes[tmpLoc]["trains"].append(self.trnName)
    self.consist[self.conName]["trainNum"] = self.train[self.trnName]["trainNum"]
    trainDB.consists.update(self.consist)
    self.train[self.trnName]["consistNum"] = self.consist[self.conName]["consistNum"]
    trainDB.trains.update(self.train)
    return 

def initConsist(self, fkey):
    self.consist = self.files.readFile(fkey)
    self.dict2ConNam(self.consist)
    print("\ncreating consist ", self.conName)
    self.consist[self.conName]["consistNum"] = trainDB.numConsists
    #trainDB.numConsists +=1
    #if mVars.prms["dbgTrnInit"]: print("consistDict: ", self.consist)
    return

