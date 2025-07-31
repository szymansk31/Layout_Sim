

import random
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from locProc import locProc
from carProc import carProc
from display import dispItems

locProcObj = locProc()
carProcObj = carProc()
dispObj    = dispItems()


dbgLocal = 1

class classCars():
    
    def __init__(self):
        pass
        
    
    def initClassPrms(self, loc, train):
        #form destination list
        self.thisLocDests = locProcObj.locDests(loc)
        self.rate = mVars.geometry[loc]["classRate"]
        
        #form train and location dict stems
        self.locStem = locs.locDat[loc]
        self.trainStem = trainDB.trains[train]
        self.type = self.locStem["type"]
        
        #form consist stem
        self.consistNam = trainDB.getConNam(train)
        self.consistNum = self.consistNam[5:]
        self.consistStem = trainDB.consists[self.consistNam]["stops"]
        return

    def printClassInfo(self, funcName, thisTrack, dest):
        print(funcName, "ydtrainNam: ", self.ydTrainNam, "numCars: ", 
              self.trainStem["numCars"] , 
        ",\n consist: ", trainDB.consists[self.consistNam], ", destination: ", dest)
        print("buildTrain: before next build step, consist : ", 
                self.consistStem[dest],
                "\ntrack contents: ", thisTrack)

    def selCar(self, thisTrack):            
        carSel, availCars = carProcObj.carTypeSel(thisTrack)
        print(\
            ", selected cartypes: ", carSel, ", availCars: ", availCars)
        carClassType = ""
        if availCars > 0:
            carClassType = carProcObj.randomCar(carSel)
        return availCars, carClassType
        
    def track2Train(self, loc, indus, train):
        # initialize common params
        self.ydTrainNam = train
        self.initClassPrms(loc, train)
        
        trainDest = self.trainStem["finalLoc"]
        trackNam = trainDest
        if self.type == "swArea": trackNam = indus
        match self.type:
            case "yard":
                if trainDest in self.locStem["tracks"]:
                    thisTrack = self.locStem["tracks"][trainDest]
                    desTrkTots = self.locStem["destTrkTots"]
                else:
                    availCars = 0
                    return availCars, trainDest
            case "swArea":
                thisTrack = locs.locDat[loc]["industries"][indus]["pickups"]
                desTrkTots = self.locStem["indusTots"]
        print("track2Train: track ", trainDest)     
        availCars, carClassType = self.selCar(thisTrack)
        if availCars <= 0: 
            print("no more cars available in yard")
            return availCars, trainDest
        if mVars.prms["dbgYdProc"]:
            self.printClassInfo(self.track2Train.__name__, thisTrack,
                trainDest)
        
        #if self.locStem["destTrkTots"][trainDest] == 0: return
        carsClassed = 0
        while ((carsClassed < self.rate) and (availCars > 0)):
            availCars, carClassType = self.selCar(thisTrack)
            carsClassed +=1
            if thisTrack[carClassType] >0:
                thisTrack[carClassType] -=1
                desTrkTots[trackNam] -=1
                self.consistStem[trainDest][carClassType] +=1
                self.trainStem["numCars"] +=1
                availCars -=1
            
        try:
        #    trainDB.consists[self.consistNum]["stops"][loc] = self.consistStem[trainDest]
        #    self.locStem["tracks"][trainDest] = thisTrack
            pass
        except:
            pass
        if mVars.prms["dbgYdProc"]: print("buildTrain: after build step, consist : ", 
                self.consistStem[trainDest],
                "\ntrack contents: ", thisTrack)
        
        return availCars, trainDest

    def randomTrack(self, weights):
        return ''.join(random.choices(self.thisLocDests, weights))

    def setWeights(self):
        # don't allow cars going to a train's destination
        # to be switched out of train.  Do this by setting 
        # weight to zero
        #
        weights = []
        for dest in self.thisLocDests:
            if dest in self.trainStem["stops"]:
                weights.append(0)
            else: weights.append(1)
        
        wtSum = sum(weights)
        weights = [weight/wtSum for weight in weights]
        print("dests, weights: ", self.thisLocDests, weights)
        return weights
        

    def train2Track(self, loc, train):
        # initialize common params
        self.initClassPrms(loc, train)
        weights = self.setWeights()
        #if mVars.prms["dbgYdProc"]:
        #    self.printClassInfo(self.train2Track.__name__, numCars, 
        #                        thisTrack, trainDest)

        if mVars.prms["dbgYdProc"]: print("train2Track: ", train, "consist: ", trainDB.consists[self.consistNam])

        carsClassed = 0
        match self.type:
            case "yard":
                destTrkSel = self.randomTrack(weights)
                destTrkTots = locs.locDat[loc]["destTrkTots"][destTrkSel]
                destTrack = locs.locDat[loc]["tracks"][destTrkSel]
            case "swArea":
                destTrkTots = locs.locDat[loc]["numOffspot"]
                destTrack = locs.locDat[loc]["offspot"]
                
        print("train2Track: train ", train)
        availCars, carClassType = self.selCar(self.consistStem[loc])
        if availCars <= 0: 
            print("no more cars available in train")
            return availCars

        while ((carsClassed < self.rate) and (availCars > 0)):
            availCars, carClassType = self.selCar(self.consistStem[loc])
            carsClassed +=1
        # remove cars from consist and assign to destination track
            if self.consistStem[loc][carClassType] >0:
                self.consistStem[loc][carClassType] -=1
                self.trainStem["numCars"] -=1
                destTrkTots +=1
                destTrack[carClassType] +=1
                availCars -=1
            
            if dbgLocal: print("train2Track: after while loop: availCars = ", 
                               availCars, ", ydTrainNam = ", train)

        try:
            trainDB.consists[self.consistNum]["stops"][loc] = self.consistStem[loc]
        except:
            pass

        return availCars
    
    def train2Indus(self, loc, indus, train):
        # initialize common params
        self.initClassPrms(loc, train)
        indusStem = locs.locDat[loc]["industries"]
        destTrack = indusStem[indus]["leave"]

        #if mVars.prms["dbgYdProc"]:
        #    self.printClassInfo(self.train2Track.__name__, numCars, 
        #                        thisTrack, trainDest)
        print("check cars in train for this swArea")
        carSet, availCars = carProcObj.carTypeSel(self.consistStem[loc])
        print("train2Indus: industry ", indus, 
              ", carTypes in train: ", carSet, ", availCars: ", availCars)
        if availCars <= 0: 
            print("no more cars in train")
            return availCars, nSpotCars
        print("check cars needed by industry (\"spot\" dict)")
        spotSet, nSpotCars = carProcObj.carTypeSel(indusStem[indus]["spot"])
        print("train2Indus: industry ", indus, 
              ", carTypes requested: ", spotSet, ", nSpotCars: ", availCars)
        if nSpotCars <= 0: 
            print("no more car spots available")
            return availCars, nSpotCars

        spotAndAvail = [1 if x != 0 and y != 0 else 0 for x, y in zip(carSet, spotSet)]
        nSpotAvail = sum(spotAndAvail)

        if mVars.prms["dbgYdProc"]: print("train2Track: #car types requested by \"spot\" and on train:", nSpotAvail, "spotAndAvail: ", spotAndAvail)

        carsClassed = 0
        while ((carsClassed < self.rate) and (nSpotAvail > 0)):

            carClassType = carProcObj.randomCar(spotAndAvail)
            carClassIDX = mVars.carTypes.index(carClassType)
            carsClassed +=1
        # remove cars from consist and drop at industry
            if self.consistStem[loc][carClassType] >0:
                # remove car from train
                self.consistStem[loc][carClassType] -=1
                self.trainStem["numCars"] -=1
                # add to indus track
                destTrack[carClassType] +=1
                # reduce requested cars
                indusStem[indus]["spot"][carClassType] -=1
               # destTrack = self.randomTrack(weights)
                # add to indus track total
                locs.locDat[loc]["indusTots"][indus] +=1
                nSpotAvail -=1
                availCars -=1
                # next block removes a carClassType from avail to switch list
                # after requested # of cars ot that type are spotted
                if indusStem[indus]["spot"][carClassType] == 0:
                    spotAndAvail[carClassIDX] = 0
            
        if dbgLocal: print("train2Track: after while loop: availCars = ", 
            availCars, ", nSpotAvail ", nSpotAvail)

        try:
            trainDB.consists[self.consistNum]["stops"][loc] = self.consistStem[loc]
        except:
            pass

        return availCars, nSpotCars, nSpotAvail
    
