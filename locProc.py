import numpy as np
import json
import random
from mainVars import mVars
from trainProc import trainDB
from layoutGeom import geom
from gui import gui
from layoutGeom import locGeom
 
dbgLocal = 1      
#=================================================
class locs():
    locDat = {}
#=================================================
class locProc():
    firstPass = 0
    trnDispCnt = 0
    
    def __init__(self):
        self.thisLoc = {}
        self.thisConsist = {}
        self.bldConsist = {}
        self.actionList = ["brkDnTrn", "swTrain", "bldTrn", "classCars", "servIndus", "misc"]
        #self.weights = [0.18, 0.18, 0.18, 0.18, 0.18, 0.1]
        self.weights = [0.5, 0, 0.5, 0, 0, 0]
        self.ydTrains = {"brkDnTrn": [], "swTrain": [], "bldTrn": []}
        self.thisLocDests = []
        self.localText = any
        locGeomObj = locGeom()
        locGeomObj.initLocText()
    #classmethod:
    
    def initLocDicts(self):
        from fileProc import readFiles
        files = readFiles()
        print("initializing location dicts: ")
        locs.locDat = files.readFile("locationFile")
        for loc in locs.locDat:
            self.countCars(loc)
        
    def countCars(self, loc):
        locDictStem = locs.locDat[loc]
        for dest in locDictStem["trackTots"]:
            for destTrack in locDictStem["tracks"]:
                for carType in locDictStem["tracks"][destTrack]:
                    locDictStem["trackTots"][dest] = locDictStem["trackTots"][dest]\
                        + locDictStem["tracks"][destTrack][carType]

    
    def randomTrack(self):
        return ''.join(random.choice(self.thisLocDests))

    def yardCalcs(self, thisloc, loc):
        self.thisLoc = thisloc
        self.thisLocDests = []
        if mVars.prms["dbgYdProc"]: print("entering yardCalcs: locdat: "
                    , locs.locDat[loc])
        for dest in locs.locDat[loc]["trackTots"]:
            self.thisLocDests.append(dest)
        #if mVars.prms["\ndbgYdProc"]: print("yardCalcs: thisLoc ", thisloc)
        self.analyzeTrains(loc)
        if mVars.prms["dbgYdProc"]: print("trains analyzed: ydTrains: ", self.ydTrains)

        self.dispLocDat(loc)
        choice = random.choices(self.actionList, weights=self.weights, k=1)
        choice = ''.join(choice)
        if mVars.prms["dbgYdProc"]: print("\nchoice: ", choice)
        match choice:
            case "brkDnTrn":
                self.brkDownTrain(loc)
                if mVars.prms["dbgYdProc"]: 
                    if dbgLocal: print("after brkDnTrn: consist: ", 
                    self.thisConsist)
                    if dbgLocal: print("this location trackTots: ", locs.locDat[loc]["trackTots"])
                pass
            case "swTrain":
                pass
            case "bldTrn":
                self.buildTrain(loc)
                pass
            case "classCars":
                pass
            case "servIndus":
                pass
            case "misc":
                pass
        self.dispTrnInLoc(loc)
            
    def analyzeTrains(self, loc):
        self.ydTrains = {"brkDnTrn": [], "swTrain": [], "buildTrain": []}

        for trainNam in locs.locDat[loc]["trains"]:
            match trainDB.trains[trainNam]["status"]:
                case "terminate":
                    if trainNam not in self.ydTrains["brkDnTrn"]:
                        self.ydTrains["brkDnTrn"].append(trainNam)
                case "dropPickup":
                    if trainNam not in self.ydTrains["swTrain"]:
                        self.ydTrains["swTrain"].append(trainNam)
                case "building":
                    if trainNam not in self.ydTrains["swTrain"]:
                        self.ydTrains["buildTrain"].append(trainNam)

    
    def dispLocDat(self, loc):
        idx = 0
        for track in locs.locDat[loc]["tracks"]:
            text = locs.locDat[loc]["tracks"][track]
            x = (gui.guiDict[loc]["x0"] + gui.guiDict[loc]["x1"])*0.5
            y = gui.guiDict[loc]["y0"] + 120 + 24*idx
            if locProc.firstPass <3:
                gui.C.create_text(x, y, text=track, font=("Arial", 8))
                locGeom.locTextID[loc]["tracks"][track]["textObjID"] = \
                    gui.C.create_text(x+5, y+12, text=text, font=("Arial", 8))
            else:
                gui.C.delete(locGeom.locTextID[loc]["tracks"][track]["textObjID"])
                locGeom.locTextID[loc]["tracks"][track]["textObjID"] = \
                    gui.C.create_text(x+5, y+12, text=text, font=("Arial", 8))
            idx +=1
        locProc.firstPass +=1
        pass
    
    def dispTrnInLoc(self, loc):
        idx = 0
        for train in locs.locDat[loc]["trains"]:
            consistNum = trainDB.trains[train]["consistNum"]
            consistNam = "consist"+str(consistNum)
            text = trainDB.consists[consistNam]["stops"]
            x = (gui.guiDict[loc]["x0"] + gui.guiDict[loc]["x1"])*0.5
            y = gui.guiDict[loc]["y0"] + 120+96 + 24*idx
            if trainDB.trains[train]["firstDisp"]:
                gui.C.create_text(x, y, text=train, font=("Arial", 8))
                trainDB.trains[train]["firstDisp"] = 0
            gui.C.delete(locGeom.locTextID[loc]["locTrnTxtID"])
            locGeom.locTextID[loc]["locTrnTxtID"] = \
                    gui.C.create_text(x+5, y+12, text=text, font=("Arial", 8))
            idx +=1
        locProc.trnDispCnt +=1
        pass
        
    def brkDownTrain(self, loc):
        from carProc import carProc
        carProcObj = carProc()
        rate = mVars.geometry[loc]["classRate"]
        for ydtrainNam in self.ydTrains["brkDnTrn"]:
            consistNum = trainDB.trains[ydtrainNam]["consistNum"]
            consistNam = "consist"+str(consistNum)
            self.thisConsist = trainDB.consists[consistNam]["stops"][loc]
            if mVars.prms["dbgYdProc"]: print("consist core: ", self.thisConsist)
            
            carSel, typeCount = carProcObj.carTypeSel(self.thisConsist)
            if dbgLocal: print("brkDnTrn: carSel: ", carSel)
            #if typeCount <= 0: return

            idx = 0
            while ((idx < rate) and (typeCount > 0)):
                carClassType = carProcObj.randomCar(carSel)
                idx +=1
            # remove cars from consist and assign to destination trackTots
                if self.thisConsist[carClassType] >0:
                    self.thisConsist[carClassType] = self.thisConsist[carClassType] - 1
                    destTrack = self.randomTrack()
                    locs.locDat[loc]["trackTots"][destTrack] +=1
                    locs.locDat[loc]["tracks"][destTrack][carClassType] +=1
                    typeCount -=1
            
            if dbgLocal: print("brkDownTrain: after while loop: typeCount = ", typeCount, ", ydTrainNam = ", ydtrainNam)
            #if ydtrainNam in self.ydTrains["brkDnTrn"]: print("found ydtrainNam")
            if typeCount == 0:
                #remove train name from ydTrains and locs.locData
                self.rmTrnFromLoc("brkDnTrn", loc, ydtrainNam)
                trainDB.trains.pop(ydtrainNam)

        try:
            trainDB.consists[consistNum]["stops"][loc] = self.thisConsist
        except:
            pass

    def rmTrnFromLoc(self, action, loc, ydtrainNam):
        index = self.ydTrains[action].index(ydtrainNam)
        self.ydTrains[action].pop(index)
        if dbgLocal: print("after removal: ydTrains: ", self.ydTrains)
        
        index = locs.locDat[loc]["trains"].index(ydtrainNam)
        locs.locDat[loc]["trains"].pop(index)
        
    def buildTrain(self, loc):
        numCarsAvail = 0
        
        #if mVars.prms["dbgYdProc"]: print("bldTrn: number of cars available: ", numCarsAvail)
        # yard has no train undergoing build
        if not self.ydTrains["buildTrain"]:
            
            self.buildNewTrain(loc)
            
            
        # yard has train building; add cars to it
        # single train is max number building in a yard
        else:         
            self.add2Train(loc)  
            ydtrainNam =  ''.join(self.ydTrains["buildTrain"])

            if trainDB.trains[ydtrainNam]["numCars"] >= mVars.prms["trainSize"]*0.7:
                # train has reached max size
                trainDB.trains[ydtrainNam]["status"] = "ready2Leave"
                route4newTrn = self.findRoutes(loc, ydtrainNam)
                trainDB.trains[ydtrainNam]["currentLoc"] = route4newTrn
                mVars.routes[route4newTrn]["trains"].append(ydtrainNam)
                if mVars.prms["dbgYdProc"]: print("train",ydtrainNam," built: "
                                ,trainDB.trains[ydtrainNam],
                                ", route: ", mVars.routes[route4newTrn])
                self.rmTrnFromLoc("buildTrain", loc, ydtrainNam)


    def findRoutes(self, loc, ydtrainNam):
        for routeNam in mVars.geometry[loc]["routes"]:
            if mVars.routes[routeNam]["origin"] == loc and \
                mVars.routes[routeNam]["dest"] == trainDB.trains[ydtrainNam]["finalLoc"]:
                return routeNam

                            
    def buildNewTrain(self, loc):
        genExp = (trackTot for trackTot in locs.locDat[loc]["trackTots"] if "indust" not in trackTot)
        for trackTots in genExp:
            if locs.locDat[loc]["trackTots"][trackTots] >= mVars.prms["trainSize"]*0.5:
                trainObj = trainDB()
                trnName, conName = trainObj.newTrain()

                trainDB.trains[trnName].update( {
                    "status": "building",
                    "origLoc": loc,
                    "finalLoc": trackTots,
                    "currentLoc": loc,
                    "numStops": 1,
                    "stops": [trackTots],
                    "color": trainDB.colors()           
                        })
                trainDB.consists[conName].update({
                    "stops": {trackTots:{"box": 0, "tank": 0,"rfr": 0, "hop": 0, 
                    "gons": 0, "flats": 0, "psgr": 0}  }
                })
                
                print("new train: ", trnName, ": ", trainDB.trains[trnName])
                print("new consist: ", conName, ":", trainDB.consists[conName])
                self.ydTrains["buildTrain"].append(trnName)
                locs.locDat[loc]["trains"].append(trnName)
                return

    
    def add2Train(self, loc):
        from carProc import carProc
        carProcObj = carProc()
        rate = mVars.geometry[loc]["classRate"]

        ydtrainNam =  ''.join(self.ydTrains["buildTrain"])
        trainDest = trainDB.trains[ydtrainNam]["finalLoc"]
        
        consistNum = trainDB.trains[ydtrainNam]["consistNum"]
        consistNam = "consist"+str(consistNum)
        numCars = trainDB.trains[ydtrainNam]["numCars"]
        print("building train: ", ydtrainNam, "numCars: ", numCars , ", consist: ", trainDB.consists[consistNam], ", destination: ", trainDest)
        self.bldConsist = trainDB.consists[consistNam]["stops"][trainDest]
        thisTrack = locs.locDat[loc]["tracks"][trainDest]
        
        if mVars.prms["dbgYdProc"]: print("bldTrn: before next build step, consist : ", 
                self.bldConsist,
                "\ntrack contents: ", thisTrack)
        
        if locs.locDat[loc]["trackTots"][trainDest] == 0: return
        carSel, typeCount = carProcObj.carTypeSel(thisTrack)
        carClassType = carProcObj.randomCar(carSel)
        carsClassed = 0
        while ((carsClassed < rate) and (typeCount > 0)):
            #trainDB.trains[]
            carsClassed +=1
            if thisTrack[carClassType] >0:
                thisTrack[carClassType] -=1
                locs.locDat[loc]["trackTots"][trainDest] -=1
                self.bldConsist[carClassType] +=1
                trainDB.trains[ydtrainNam]["numCars"] +=1
                typeCount -=1

        try:
            trainDB.consists[consistNum]["stops"][loc] = self.bldConsist
            locs.locDat[loc]["tracks"][trainDest] = thisTrack
        except:
            pass
        if mVars.prms["dbgYdProc"]: print("bldTrn: after build step, consist : ", 
                self.bldConsist,
                "\ntrack contents: ", thisTrack)
            
    def classCars(self):
        pass
    def servIndus(self):
        pass
    # calc trains that arrive, trains ready to leave (and do they?)
    # cars classified; need a dict with all car types, next dest (track or 
    # loc), status (ready to classify, classified, in arriving train)
        #self.trainOut = self.rateClassification*self.fracTrainBuild/mVars.trainSize


