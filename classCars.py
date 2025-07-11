

import random
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from locProc import locProc
from carProc import carProc
locProcObj = locProc()
carProcObj = carProc()

dbgLocal = 1

class classCars():
    
    def __init__(self, loc):
        #form destination list
        self.thisLocDests = locProcObj.locDests(loc)
        self.rate = mVars.geometry[loc]["classRate"]
        
        #form train and location dict stems
        self.ydtrainNam =  ''.join(self.ydtrains["buildTrain"])
        self.locStem = locs.locDat[loc]
        self.trainStem = trainDB.trains[self.ydtrainNam]
        
        #form consist stem
        self.consistNum = self.trainStem["consistNum"]
        self.consistNam = "consist"+str(self.consistNum)
        self.consistStem = trainDB.consists[self.consistNam]["stops"]
        pass
    
    def randomTrack(self):
        return ''.join(random.choice(self.thisLocDests))

    
    def track2Train(self, loc):
        # these two variables will depend on whether train or 
        # yard tracks are gettting cars
        trainDest = self.trainStem["nextLoc"]
        numCars = self.trainStem["numCars"]
        print("adding to train: ", self.ydtrainNam, "numCars: ", numCars , 
              ", consist: ", trainDB.consists[self.consistNam], ", destination: ", trainDest)
        thisTrack = self.locStem["tracks"][trainDest]
        
        if mVars.prms["dbgYdProc"]: print("buildTrain: before next build step, consist : ", 
                self.bldConsist,
                "\ntrack contents: ", thisTrack)
        
        if self.locStem["trackTots"][trainDest] == 0: return
        carSel, typeCount = carProcObj.carTypeSel(thisTrack)
        
        carsClassed = 0
        while ((carsClassed < self.rate) and (typeCount > 0)):

            carClassType = carProcObj.randomCar(carSel)
            carsClassed +=1
            if thisTrack[carClassType] >0:
                thisTrack[carClassType] -=1
                self.locStem["trackTots"][trainDest] -=1
                self.consistStem[trainDest][carClassType] +=1
                self.trainStem["numCars"] +=1
                typeCount -=1

        try:
            trainDB.consists[self.consistNum]["stops"][loc] = self.consistStem[trainDest]
            self.locStem["tracks"][trainDest] = thisTrack
        except:
            pass
        if mVars.prms["dbgYdProc"]: print("buildTrain: after build step, consist : ", 
                self.bldConsist,
                "\ntrack contents: ", thisTrack)


    def train2Track(self, loc):

        for ydtrainNam in self.ydtrains["brkDnTrn"]:

            if mVars.prms["dbgYdProc"]: print("brkDownTrain: ", ydtrainNam, "consist: ", trainDB.consists[consistNam])
            self.consistStem = trainDB.consists[self.consistNam]["stops"][loc]
            
            carSel, typeCount = carProcObj.carTypeSel(self.consistStem)
            if dbgLocal: print("brkDnTrn: carSel: ", carSel)

            carsClassed = 0
            while ((carsClassed < self.rate) and (typeCount > 0)):

                carClassType = carProcObj.randomCar(carSel)
                carsClassed +=1
            # remove cars from consist and assign to destination trackTots
                if self.consistStem[carClassType] >0:
                    self.consistStem[carClassType] = self.consistStem[carClassType] - 1
                    destTrack = self.randomTrack()
                    locs.locDat[loc]["trackTots"][destTrack] +=1
                    locs.locDat[loc]["tracks"][destTrack][carClassType] +=1
                    typeCount -=1
            
            if dbgLocal: print("train2Track: after while loop: typeCount = ", typeCount, ", ydTrainNam = ", ydtrainNam)

            if typeCount == 0:
                #remove train name from ydTrains and locs.locData
                self.locProcObj.rmTrnFromLoc("brkDnTrn", loc, self.ydtrains, ydtrainNam)
                trainDB.trains.pop(ydtrainNam)

        try:
            trainDB.consists[self.consistNum]["stops"][loc] = self.consistStem
        except:
            pass
