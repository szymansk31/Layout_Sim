
from stateVars import locs, trainDB
from carProc import carProc
carProcObj = carProc()

class classify():
    
    def __init__(self):
        self.dbgLocal = 1
        pass
    classifyDict = {
        "consistIn": thisConsist,
        "consistOut": track,
        "loc": loc,
        "action": action,
        "ydtrains": ydtrains,
        "ydtrainNam": ydtrainNam
    }
    def classCars(self, classifyDict):
        consist = classifyDict["consist"]
        loc = classifyDict["loc"]
        action = classifyDict["action"]
        ydtrains = classifyDict["ydtrains"]
        ydtrainNam = classifyDict["ydtrainNam"]
        rate = locs.locDat[loc]["classRate"]
        
        carSel, typeCount = carProcObj.carTypeSel(consist)
        if self.dbgLocal: print("classCars: carSel: ", carSel)
        #if typeCount <= 0: return

        idx = 0
        while ((idx < rate) and (typeCount > 0)):
            carClassType = carProcObj.randomCar(carSel)
            idx +=1
        # remove cars from consist and assign to destination trackTots
            if consist[carClassType] >0:
                consist[carClassType] = consist[carClassType] - 1
                destTrack = self.randomTrack()
                locs.locDat[loc]["trackTots"][destTrack] +=1
                locs.locDat[loc]["tracks"][destTrack][carClassType] +=1
                typeCount -=1
        
        if self.dbgLocal: print("classCars: after while loop: typeCount = ", typeCount, ", ydTrainNam = ", ydtrainNam)

        if typeCount == 0:
            #remove train name from ydTrains and locs.locData
            self.locProcObj.rmTrnFromLoc("brkDnTrn", loc, self.ydtrains, ydtrainNam)
            trainDB.trains.pop(ydtrainNam)
