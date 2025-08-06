
from mainVars import mVars
from stateVars import trainDB

class printMethods():
    
    def __init__(self):
        pass

    def printTrainInfo(self, train):
        trainStem = trainDB.trains[train]
        numCars = trainStem["numCars"]
        currentLoc = trainStem["currentLoc"]
        nextLoc = trainStem["nextLoc"]
        finalLoc = trainStem["finalLoc"]
        origLoc = trainStem["origLoc"]
        status = trainStem["status"]
        direction = trainStem["direction"]
        if mVars.prms["dbgLoop"]: print (
            "Before proc: ", train, ", #cars: ", numCars,
            "currL: ", currentLoc, ", nextL: ", nextLoc, 
            ", origL: ", origLoc, 
            ", finL: ", finalLoc, ", dir: ", direction,
            "status: ", status)

    def writeTrainInfo(self, file, train):
        trainStem = trainDB.trains[train]
        numCars = trainStem["numCars"]
        currentLoc = trainStem["currentLoc"]
        nextLoc = trainStem["nextLoc"]
        finalLoc = trainStem["finalLoc"]
        origLoc = trainStem["origLoc"]
        status = trainStem["status"]
        direction = trainStem["direction"]
        if mVars.prms["dbgLoop"]: 
            file.write (
            "\nStart of Time Step: " + train + ", #cars: " + str(numCars) + 
            ", currL: " + currentLoc + ", nextL: " + nextLoc + 
            ", origL: " + origLoc + 
            ", finL: " + finalLoc + ", dir: " + direction + 
            ", status: " + status)

