import numpy as np
from mainVars import *
import random
            
#=================================================
class carProc():
    
    def __init__(self):
        pass
    
                    
    def carTypeSel(self, consist):
        carSelDict = {'box': 0, 'tank': 0, 'rfr': 0, 'hop': 0, 'gons': 0, 'flats': 0, 'psgr': 0}
        carSelList = [0 for _ in range(mVars.numCarTyp)]  # Creates a list like [0, 0, 0, 0, 0]

        availCars = 0
        for cartyp in list(consist.keys()):
            carSelDict[cartyp] = consist[cartyp]
            availCars += consist[cartyp]
        idx = 0
        print("carSelDict: ", carSelDict)
        if availCars != 0:
            for keys in carSelDict.keys():
                carSelList[idx] = carSelDict[keys]/availCars
                idx +=1
        print("carSelList: ", carSelList, ", availCars: ", availCars)
        return carSelList, availCars
        
    def randomCar(self, carSelList):
        tmpCarClass = random.choices(mVars.carTypes, weights=carSelList, k=1)
        return ''.join(tmpCarClass)

     
