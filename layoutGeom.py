
import math
from mainVars import *
from stateVars import locs, routeCls
from gui import gui    
from coords import transForms

            
#=================================================
class geom():
    layoutLocsRoutes = {}
    locList = []

    def __init__(self):
        pass
    
    def locListInit(self, locStem):
        for loc in locStem:
            geom.locList.append(loc)
        if mVars.prms["dbgGeom"]: print("locList: ", geom.locList)
    
class routeGeom():
    def __init__(self):
        pass
    
    def initRoutes(self, guiDict):
        from fileProc import readFiles
        files = readFiles()
        print("\ninitializing route dicts: ")

        routeCls.routes = files.readFile("routeFile")
        for routeNam in routeCls.routes:            
            westObj = guiDict[routeNam]["westObj"]
            eastObj = guiDict[routeNam]["eastObj"]
            routeCls.routes[routeNam]["westObj"] = westObj
            routeCls.routes[routeNam]["eastObj"] = eastObj
            routeCls.routes[routeNam]["transTime"] = guiDict[routeNam]["transTime"]
            routeCls.routes[routeNam]["trnLabelTag"] = routeNam+"trnLblTag"
            routeCls.routes[routeNam]["trains"] = []

            # route lines are drawn west-to-east; train locs follow
            routeCls.routes[routeNam].update(self.routeLine(routeNam, guiDict))
            routeCls.routes[routeNam].update(self.trnsOnRoutes(routeCls.routes[routeNam], routeNam, guiDict))

            if mVars.prms["dbgGeom"]: print("\ninitRoutes: newRoute: ", routeCls.routes[routeNam])
            
        locStem = locs.locDat
        for loc in locStem:
            if (loc == westObj) or (loc == eastObj):
                rtList = locStem[loc].get("routes")
                rtList.append(routeNam)
                locStem[loc]["routes"] = rtList
        if mVars.prms["dbgGeom"]: print("\ninitRoutes: locStem for loc: ", loc, "is", locStem[loc])
        return

    def trnsOnRoutes(self, routeDict, rtNam, guiDict):
        westObj = guiDict[guiDict[rtNam]["westObj"]]
        xDist, yDist, lineLen = self.rtGeomCalcs(rtNam, guiDict)
        yRoute = (westObj["y0"] + westObj["y1"])*0.5
        height = westObj["y1"] - westObj["y0"]
    
        #if mVars.prms["dbgGeom"]: print("trnsOnRoutes: trnrtLength: ", 
        #        trainParams.trnrtLength, "eastObj[x0]", eastObj["x0"])

        routeDictOut = {
            "yTrn": yRoute - height*0.25,
            "yTrnCon": westObj["y0"] - 5,
            "rtLength": lineLen,
            "distPerTime": lineLen/routeDict["transTime"]
                    }
        return routeDictOut

    # routeLine draws lines to represent all routes between endpoints
    # no regard for direction, just want the lines between locs
    # train gui data is initialized in trnsOnRoutes
    def routeLine(self, rtNam, guiDict):
        xDist, yDist, lineLen = self.rtGeomCalcs(rtNam, guiDict)
        westObj = guiDict[guiDict[rtNam]["westObj"]]
        eastObj = guiDict[guiDict[rtNam]["eastObj"]]
        y0 = (westObj["y0"] + westObj["y1"])*0.5
        y1 = (eastObj["y0"] + eastObj["y1"])*0.5
        
        routeDictOut = {
            "x0": westObj["x1"],
            "x1": eastObj["x0"],
            "y0": y0,
            "y1": y1,
            "cosTh": round(xDist/lineLen, 3),
            "sinTh": round(yDist/lineLen, 3)
                  }
        
        return routeDictOut

    def rtGeomCalcs(self, rtNam, guiDict):        
        westObj = guiDict[guiDict[rtNam]["westObj"]]
        eastObj = guiDict[guiDict[rtNam]["eastObj"]]
        y0 = (westObj["y0"] + westObj["y1"])*0.5
        y1 = (eastObj["y0"] + eastObj["y1"])*0.5
        
        yDist = abs(y1 - y0)
        xDist = abs(eastObj["x0"] - westObj["x1"])
        lineLen = math.sqrt(xDist*xDist+yDist*yDist)
            
        return xDist, yDist, lineLen

