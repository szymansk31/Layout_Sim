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
    

    def xPlot2xRoute(self, route, train):
        cosTh = routeCls.routes[route]["cosTh"]
        sinTh = routeCls.routes[route]["sinTh"]
        x = trainDB.trains[train]["coord"]["xPlot"]
        y = trainDB.trains[train]["coord"]["yPlot"]
        xRoute = x*cosTh + y*sinTh
        yRoute = y*cosTh - x*sinTh    
        trainDB.trains[train]["coord"]["xRoute"] = round(xRoute, 2)
        trainDB.trains[train]["coord"]["yRoute"] = round(yRoute, 2)
        
    def xRoute2xPlot(self, route, train):
        cosTh = routeCls.routes[route]["cosTh"]
        sinTh = routeCls.routes[route]["sinTh"]
        xRoute = trainDB.trains[train]["coord"]["xRoute"]
        yRoute = trainDB.trains[train]["coord"]["yRoute"]
        if trainDB.trains[train]["direction"] == "east":
            xOffset = routeCls.routes[route]["x0"]
            yOffset = routeCls.routes[route]["y0"]
        else:
            xOffset = routeCls.routes[route]["x1"]
            yOffset = routeCls.routes[route]["y1"]
        x = xRoute*cosTh - yRoute*sinTh + xOffset
        y = -(yRoute*cosTh + xRoute*sinTh) + yOffset - gui.guiDict["locDims"]["height"]*0.25
        trainDB.trains[train]["coord"]["xPlot"] = round(x, 2)
        trainDB.trains[train]["coord"]["yPlot"] = round(y, 2)


