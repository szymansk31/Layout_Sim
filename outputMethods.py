
from mainVars import mVars
from stateVars import trainDB, routeCls
from dispatch import rtCaps

class printMethods():
    
    def __init__(self):
        self.rtCapsObj =rtCaps() 
        pass

    def printTrainInfo(self, trainNam):
        trainStem = trainDB.trains[trainNam]
        numCars = trainStem["numCars"]
        currentLoc = trainStem["currentLoc"]
        nextLoc = trainStem["nextLoc"]
        finalLoc = trainStem["finalLoc"]
        origLoc = trainStem["origLoc"]
        status = trainStem["status"]
        direction = trainStem["direction"]
        if mVars.prms["dbgLoop"]: print (
            "Before proc: ", trainNam, ", #cars: ", numCars,
            "currL: ", currentLoc, ", nextL: ", nextLoc, 
            ", origL: ", origLoc, 
            ", finL: ", finalLoc, ", dir: ", direction,
            "status: ", status)

    def writeTrainInfo(self, file, trainNam):
        trainStem = trainDB.trains[trainNam]
        numCars = trainStem["numCars"]
        currentLoc = trainStem["currentLoc"]
        nextLoc = trainStem["nextLoc"]
        finalLoc = trainStem["finalLoc"]
        origLoc = trainStem["origLoc"]
        status = trainStem["status"]
        direction = trainStem["direction"]
        if mVars.prms["dbgLoop"]: 
            file.write (
            "\nStart of Time Step: " + trainNam + ", #cars: " + str(numCars) + 
            ", currL: " + currentLoc + ", nextL: " + nextLoc + 
            ", origL: " + origLoc + 
            ", finL: " + finalLoc + ", dir: " + direction + 
            ", status: " + status)

    def printRtCaps(self):
        print("\nrtCaps.rtCap: ")
        for route in rtCaps.rtCap:
            print(route, ": ", "trains: ", 
                  routeCls.routes[route]["trains"],
                  rtCaps.rtCap[route])
            
    def writeRtCaps(self, file, route):
        file.write("\nrtCaps.rtCap: ")
        file.write("\n" + route + ": " +  \
            "trains: " + str(routeCls.routes[route]["trains"]) + \
            str(rtCaps.rtCap[route]))
       