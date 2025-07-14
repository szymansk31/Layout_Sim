import numpy as np
from mainVars import *
import random
            
#=================================================
class carProc():
    
    def __init__(self):
        pass
    
    
    def procCarInfo(self, carDict):
        for loc in mVars.geometry:
            for carType in mVars.carTypes:
                for nextLoc in mVars.geometry:      #nextLoc is a new name for a second loc var
                    carDict[loc][carType]["nextDest"].update({nextLoc: 0})
                #print("carDict for carType: ", carType, ": ", carDict[loc][carType])
                    
    def carTypeSel(self, consist):
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
        tmpCarClass = random.choices(mVars.carTypes, weights=carSelList, k=1)
        return ''.join(tmpCarClass)

     
