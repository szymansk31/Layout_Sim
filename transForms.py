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
    

    def x2XPrime(self, route):
        coord = {}
        cosTh = routeCls[route]["coord"]["cosTh"]
        sinTh = routeCls[route]["coord"]["sinTh"]
        coord["xP"] = coord["x"]*cosTh + coord["y"]*sinTh
        coord["yP"] = coord["y"]*cosTh - coord["x"]*sinTh    
        
    def xPrime2X(self, route):
        coord = {}
        cosTh = routeCls[route]["coord"]["cosTh"]
        sinTh = routeCls[route]["coord"]["sinTh"]
        coord["x"] = coord["xP"]*cosTh - coord["yP"]*sinTh
        coord["y"] = coord["yP"]*cosTh + coord["xP"]*sinTh