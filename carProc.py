import numpy as np
from mainVars import *
import random
            
#=================================================
class carProc():
    
    def __init__(self):
        pass
    
    def readCarInitInfo(self, files):
        print("\nReading initial car info from file: ", files.carDictFile)
        try: 
            jsonFile = open (files.carDictFile, "r")
            carDict = json.load(jsonFile)
            jsonFile.close()
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        #print("carDict: ", carDict)
        return carDict
    
    def procCarFileInfo(self, carDict):
        for loc in mVars.geometry:
            for carType in mVars.carTypes:
                for nextLoc in mVars.geometry:      #nextLoc is a new name for a second loc var
                    carDict[loc][carType]["nextDest"].update({nextLoc: 0})
                #print("carDict for carType: ", carType, ": ", carDict[loc][carType])
                    
    def carTypeSel(self, consist, loc):
        carSelDict = {}
        carSelList = [0 for _ in range(mVars.numCarTyp)]  # Creates a list like [0, 0, 0, 0, 0]

        typeCount = 0
        for cartyp in list(consist.keys()):
            carSelDict[cartyp] = consist[cartyp]
            typeCount += consist[cartyp]
        idx = 0
        print("carSelDict: ", carSelDict, ", typeCount: ", typeCount)
        if typeCount != 0:
            for keys in carSelDict.keys():
                carSelList[idx] = carSelDict[keys]/typeCount
                idx +=1
        return carSelList, typeCount
        
    def randomCar(self, carSelList):
        return random.choices(mVars.carTypes, weights=carSelList, k=1)
        

     
