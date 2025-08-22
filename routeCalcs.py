import random
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from display import dispItems
from dispatch import schedProc
from yardCalcs import ydCalcs
from swCalcs import swCalcs
from stagCalcs import stCalcs
from gui import gui
from coords import transForms
from dispatch import dspCh, rtCaps
from outputMethods import printMethods
        

np.set_printoptions(precision=2, suppress=True) 

class routeInit():
    
    def __init__(self):
        pass
    
class routeCalcs():
    
    def __init__(self):
        pass
    
    def calcTrnArrivalTime(self, route):
        for route in routeCls.routes:
            routeStem = routeCls.routes[route]
            for train in routeStem["trains"]:
                trainStem = trainDB.trains[train]
                dist2Go = routeStem["rtLength"] - \
                    trainStem["coord"]["xRoute"]
                time2Go = abs(dist2Go)/routeStem["distPerTime"]
                arrivalTime = mVars.time + time2Go
                trainStem["estArrTime"] = arrivalTime