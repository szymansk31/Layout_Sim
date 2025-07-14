

import random
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from locProc import locProc
from carProc import carProc
from display import dispItems
from yardCalcs import ydCalcs
locProcObj = locProc()
carProcObj = carProc()
dispObj    = dispItems()


dbgLocal = 1

class classCars():
    
    def __init__(self):
        pass
        
    
    def randomTrack(self):
        return ''.join(random.choice(self.thisLocDests))

    def initClassPrms(self, funcName, loc, lcl_ydTrain, action):
        #form destination list
        self.thisLocDests = locProcObj.locDests(loc)
        self.rate = mVars.geometry[loc]["classRate"]
        
        #form train and location dict stems
        if action == "buildTrain":
            self.ydTrainNam =  ''.join(trainDB.ydTrains[action])
        elif action == "swTrain" and funcName == "track2Train":
            self.ydTrainNam = lcl_ydTrain
        else:
            self.ydTrainNam = random.choice(trainDB.ydTrains.get(action))
        print("ydtrainNam: ", self.ydTrainNam)
        self.locStem = locs.locDat[loc]
        self.trainStem = trainDB.trains[self.ydTrainNam]
        
        #form consist stem
        self.consistNum = self.trainStem["consistNum"]
        self.consistNam = "consist"+str(self.consistNum)
        self.consistStem = trainDB.consists[self.consistNam]["stops"]
        return

    def printClassInfo(self, funcName, thisTrack, numCars, dest):
        print(funcName, "ydtrainNam: ", self.ydTrainNam, "numCars: ", numCars , 
        ", consist: ", trainDB.consists[self.consistNam], ", destination: ", dest)
        print("buildTrain: before next build step, consist : ", 
                self.consistStem[dest],
                "\ntrack contents: ", thisTrack)

    def track2Train(self, loc, train, action):
        # initialize common params
        self.initClassPrms(self.track2Train.__name__, loc,
                           train, action=action)
        dispObj.dispActionDat(loc, action, self.ydTrainNam)
        # these two variables will depend on whether train or 
        # yard tracks are gettting cars
        trainDest = self.trainStem["nextLoc"]
        thisTrack = self.locStem["tracks"][trainDest]
        
        carSel, availCars = carProcObj.carTypeSel(thisTrack)

        if availCars <= 0: return availCars, trainDest
        if mVars.prms["dbgYdProc"]:
            self.printClassInfo(self.track2Train.__name__, thisTrack,
                self.trainStem["numCars"], trainDest)
        
        #if self.locStem["trackTots"][trainDest] == 0: return
        
        carsClassed = 0
        while ((carsClassed < self.rate) and (availCars > 0)):

            carClassType = carProcObj.randomCar(carSel)
            carsClassed +=1
            if thisTrack[carClassType] >0:
                thisTrack[carClassType] -=1
                self.locStem["trackTots"][trainDest] -=1
                self.consistStem[trainDest][carClassType] +=1
                self.trainStem["numCars"] +=1
                availCars -=1

        try:
            trainDB.consists[self.consistNum]["stops"][loc] = self.consistStem[trainDest]
            self.locStem["tracks"][trainDest] = thisTrack
        except:
            pass
        if mVars.prms["dbgYdProc"]: print("buildTrain: after build step, consist : ", 
                self.consistStem[trainDest],
                "\ntrack contents: ", thisTrack)
        
        return availCars, trainDest

    def train2Track(self, loc, action):
        # initialize common params
        self.initClassPrms(self.train2Track.__name__, loc, "", action=action)
        dispObj.dispActionDat(loc, action, self.ydTrainNam)

        #if mVars.prms["dbgYdProc"]:
        #    self.printClassInfo(self.train2Track.__name__, numCars, 
        #                        thisTrack, trainDest)
        carSel, availCars = carProcObj.carTypeSel(self.consistStem[loc])
        if availCars <= 0: return availCars, self.ydTrainNam

        if mVars.prms["dbgYdProc"]: print("train2Track: ", self.ydTrainNam, "consist: ", trainDB.consists[self.consistNam])

        carsClassed = 0
        while ((carsClassed < self.rate) and (availCars > 0)):

            carClassType = carProcObj.randomCar(carSel)
            carsClassed +=1
        # remove cars from consist and assign to destination trackTots
            if self.consistStem[loc][carClassType] >0:
                self.consistStem[loc][carClassType] -=1
                destTrack = self.randomTrack()
                locs.locDat[loc]["trackTots"][destTrack] +=1
                locs.locDat[loc]["tracks"][destTrack][carClassType] +=1
                availCars -=1
            
            if dbgLocal: print("train2Track: after while loop: availCars = ", 
                               availCars, ", ydTrainNam = ", self.ydTrainNam)

        try:
            trainDB.consists[self.consistNum]["stops"][loc] = self.consistStem[loc]
        except:
            pass

        return availCars, self.ydTrainNam