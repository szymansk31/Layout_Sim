import json
from fileNameSetup import *

class mainVar:
    numYards = int
    numTowns = int
    trainSize = int
    numOperators = int
    
    def __init__(self):
        self.files = fileNames()
     
    def readParams(self):
        print("\nreading param File")
        try: 
            jsonFile = open (self.files.paramDictFile, "r")
            paramDict = json.load(jsonFile)
            jsonFile.close()
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        print("paramDict: ", paramDict)


class indices:
    def __init__(self):
        self.mainIDX = 0

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
