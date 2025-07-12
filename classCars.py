

import random
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from locProc import locProc
from carProc import carProc
from yardCalcs import ydCalcs
locProcObj = locProc()
carProcObj = carProc()

dbgLocal = 1

class classCars():
    
    def __init__(self):
        pass
    
    
    def randomTrack(self):
        return ''.join(random.choice(self.thisLocDests))

    def initClassPrms(self, loc, lcl_ydTrains, action):
        #form destination list
        self.thisLocDests = locProcObj.locDests(loc)
        self.rate = mVars.geometry[loc]["classRate"]
        
        #form train and location dict stems
        if action == "buildTrain":
            self.ydtrainNam =  ''.join(lcl_ydTrains[action])
        else:
            self.ydtrainNam = random.choice(trainDB.ydTrains.get(action))
        print("ydtrainNam: ", self.ydtrainNam)
        self.locStem = locs.locDat[loc]
        self.trainStem = trainDB.trains[self.ydtrainNam]
        
        #form consist stem
        self.consistNum = self.trainStem["consistNum"]
        self.consistNam = "consist"+str(self.consistNum)
        self.consistStem = trainDB.consists[self.consistNam]["stops"]
        pass

    def printClassInfo(self, funcName, thisTrack, numCars, dest):
        print(funcName, "ydtrainNam: ", self.ydtrainNam, "numCars: ", numCars , 
        ", consist: ", trainDB.consists[self.consistNam], ", destination: ", dest)
        print("buildTrain: before next build step, consist : ", 
                self.consistStem[dest],
                "\ntrack contents: ", thisTrack)

    def track2Train(self, loc, action):
        # initialize common params
        self.initClassPrms(loc, trainDB.ydTrains, action=action)
        # these two variables will depend on whether train or 
        # yard tracks are gettting cars
        trainDest = self.trainStem["nextLoc"]
        numCars = self.trainStem["numCars"]
        thisTrack = self.locStem["tracks"][trainDest]
        
        if mVars.prms["dbgYdProc"]:
            self.printClassInfo(self.track2Train.__name__, numCars, 
                                thisTrack, trainDest)
        
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
                self.consistStem[trainDest],
                "\ntrack contents: ", thisTrack)


    def train2Track(self, loc, action):
        # initialize common params
        self.initClassPrms(loc, trainDB.ydTrains, action=action)
        
        #if mVars.prms["dbgYdProc"]:
        #    self.printClassInfo(self.train2Track.__name__, numCars, 
        #                        thisTrack, trainDest)
        
        if mVars.prms["dbgYdProc"]: print("brkDownTrain: ", self.ydtrainNam, "consist: ", trainDB.consists[self.consistNam])
        carSel, typeCount = carProcObj.carTypeSel(self.consistStem[loc])

        carsClassed = 0
        while ((carsClassed < self.rate) and (typeCount > 0)):

            carClassType = carProcObj.randomCar(carSel)
            carsClassed +=1
        # remove cars from consist and assign to destination trackTots
            if self.consistStem[loc][carClassType] >0:
                self.consistStem[loc][carClassType] -=1
                destTrack = self.randomTrack()
                locs.locDat[loc]["trackTots"][destTrack] +=1
                locs.locDat[loc]["tracks"][destTrack][carClassType] +=1
                typeCount -=1
            
            if dbgLocal: print("train2Track: after while loop: typeCount = ", 
                               typeCount, ", ydTrainNam = ", self.ydtrainNam)

            if typeCount == 0:
                #remove train name from trainDB.ydTrains and locs.locData
                locProcObj.rmTrnFromLoc("brkDnTrn", loc, self.ydtrainNam)
                trainDB.trains.pop(self.ydtrainNam)

        try:
            trainDB.consists[self.consistNum]["stops"][loc] = self.consistStem[loc]
        except:
            pass
