import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from display import dispItems
from gui import gui
np.set_printoptions(precision=2, suppress=True) 


dbgLocal = 1   
  
#=================================================
class transForms():

    def __init__(self):
        pass
    

    def x2XPrime(self, route, coord):
        cosTh = routeCls[route]["coord"]["cosTh"]
        sinTh = routeCls[route]["coord"]["sinTh"]
        coord["xP"] = coord["x"]*cosTh + coord["y"]*sinTh
        coord["yP"] = coord["y"]*cosTh - coord["x"]*sinTh    
        
    def xPrime2X(self, route, coord):
        cosTh = routeCls[route]["coord"]["cosTh"]
        sinTh = routeCls[route]["coord"]["sinTh"]
        coord["x"] = coord["xP"]*cosTh - coord["yP"]*sinTh
        coord["y"] = coord["yP"]*cosTh + coord["xP"]*sinTh


    def distCalcs(self, rtNam, guiDict):        
        leftObj = guiDict[guiDict[rtNam]["leftObj"]]
        rtObj = guiDict[guiDict[rtNam]["rtObj"]]
        y0 = (leftObj["y0"] + leftObj["y1"])*0.5
        y1 = (rtObj["y0"] + rtObj["y1"])*0.5
        
        yDist = np.abs(y1 - y0)
        xDist = np.abs(rtObj["x0"] - leftObj["x1"])
        lineLen = np.sqrt(xDist*xDist+yDist*yDist)
            
        return xDist, yDist, lineLen
