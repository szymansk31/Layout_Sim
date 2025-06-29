import json
from fileNamesIO import *

class mVars:       #short for mainVars
    time = 0
    numOpBusy = 0
    prms = {}
    geometry = {}
    routes = {}
    carsAtLocs = {}
    carTypes = ["boxCars", "tankCars", "reefers", "hoppers", "gons", "flats", "psgr"]
    numCarTyp = len(carTypes)
    
    def __init__(self):
        pass
        #self.files = fileNames()
     
    def readParams(files):
        print("\nreading param file ", files.paramDictFile)
        try: 
            jsonFile = open (files.paramDictFile, "r")
            mVars.prms = json.load(jsonFile)
            jsonFile.close()
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        if mVars.prms["dbgPrmInit"]: print("paramDict: ", mVars.prms)


#=================================================
class carHdr:
    carType = str
    totCarType = int
    number = []
    carDesc = []
    railroad = []
    

    def __init__(self):
        car = carHdr()
        
    def fillCarInfo(self, name, carID, idx):
        self.carType = name
        self.carID = carID
        self.RR = self.railroad[idx]
        self.desc = self.carDesc[idx]
        self.carNum = self.number[idx]
        
    def defCarDict(self):
        carDict = {
            self.car.cartype : self.carType,
            
            
            
        }
        
#=================================================
class dictProc():
    shade = 0
    def __init__(self):
        pass
            
    def add2MainDict(self):
        mainDict[car.carType][car.carID] = {
                "RR" : car.RR,
                "carDesc" : car.desc,
                "carNum" : car.carNum,
                'destIDX' : 0,
                'destSet' : [" ", " "," ", " "," ", " "," ", " "," "]}

    def mainSav(self, destIDX, destNam):
        mainDict[car.carType][car.carID]["destIDX"] +=1
        mainDict[car.carType][car.carID]["destSet"][destIDX] = destNam
