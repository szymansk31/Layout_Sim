
from mainVars import mVars
from stateVars import trainDB

class printMethods():
    
    def __init__(self):
        pass

    def printTrainInfo(self, train):
        trainStem = trainDB.trains[train]
        currentLoc = trainStem["currentLoc"]
        nextLoc = trainStem["nextLoc"]
        finalLoc = trainStem["finalLoc"]
        origLoc = trainStem["origLoc"]
        status = trainStem["status"]
        direction = trainStem["direction"]
        if mVars.prms["dbgLoop"]: print (
            "Before train processing: train: ", train, 
            "currentLoc: ", currentLoc, ", nextLoc: ", nextLoc, 
            ", origLoc: ", origLoc, 
            ", finalLoc: ", finalLoc, ", direction: ", direction,
            "status: ", status)

    def writeTrainInfo(self, file, train):
        trainStem = trainDB.trains[train]
        currentLoc = trainStem["currentLoc"]
        nextLoc = trainStem["nextLoc"]
        finalLoc = trainStem["finalLoc"]
        origLoc = trainStem["origLoc"]
        status = trainStem["status"]
        direction = trainStem["direction"]
        if mVars.prms["dbgLoop"]: 
            file.write (
            "\nBefore trainProc: train: " + train +
            " currentLoc: " + currentLoc + ", nextLoc: " + nextLoc + 
            ", origLoc: " + origLoc + 
            ", finalLoc: " + finalLoc + ", dir: " + direction + 
            ", status: " + status)

