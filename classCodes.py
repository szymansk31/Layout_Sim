
import random
from stateVars import locs, trainDB
from carProc import carProc
from mainVars import mVars

carProcObj = carProc()
locProcObj = locs()

class classify():
    classifyDict = {}
    def __init__(self):
        self.dbgLocal = 1
        pass
    
    
    classifyDict = {
        "consistIn": {},
        "consistOut": {},
        "loc": "",
        "action": "",
        "ydtrains": {},
        "ydtrainNam": ""
    }
    
    def randomTrack(self):
        return ''.join(random.choice(self.thisLocDests))

    def classCars(self, classifyDict):
        trainNam = classifyDict["trainNam"]
        consistInType = classifyDict["consistInType"]
        consistOutType = classifyDict["consistOutType"]
        loc = classifyDict["loc"]
        action = classifyDict["action"]
        ydtrains = classifyDict["ydtrains"]
        ydtrainNam = classifyDict["ydtrainNam"]
        rate = mVars.geometry[loc]["classRate"]
        thisLocDests = locProcObj.locDests(loc)

        if consistOutType == "location":
            consistOutCount = locs.locDat[loc]["trackTots"]
            consistOutTypeLoc = locs.locDat[loc]["tracks"]
        else:
            consistOutCount = trainDB.trains[ydtrainNam]["numCars"]
            consistOutTypeLoc = trainDB.trains[ydtrainNam]
            
            
        carSel, typeCount = carProcObj.carTypeSel(consistIn)
        if self.dbgLocal: print("classCars: carSel: ", carSel)

        carsClassed = 0
        while ((carsClassed < rate) and (typeCount > 0)):
            carClassType = carProcObj.randomCar(carSel)
            carsClassed +=1
        # remove cars from consist and assign to destination trackTots
            if consistIn[carClassType] >0:
                consistIn[carClassType] -=1
                if consistOutType == "location":
                    destTrack = self.randomTrack()
                    consistOut[destTrack] +=1
                    consistOut["tracks"][destTrack][carClassType] +=1
                typeCount -=1
        
        if self.dbgLocal: print("classCars: after while loop: typeCount = ", typeCount, ", ydTrainNam = ", ydtrainNam)

        if typeCount == 0:
            #remove train name from ydTrains and locs.locData
            self.locProcObj.rmTrnFromLoc("brkDnTrn", loc, self.ydtrains, ydtrainNam)
            trainDB.trains.pop(ydtrainNam)
