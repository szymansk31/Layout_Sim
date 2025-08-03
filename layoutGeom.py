
import math
from mainVars import *
from stateVars import routeCls
from trainProc import trainParams
from gui import gui    
from coords import transForms

            
#=================================================
class geom():
    layoutLocsRoutes = {}
    locList = []

    def __init__(self):
        pass
    
    def locListInit(self, geometry):
        for loc in geometry:
            geom.locList.append(loc)
        if mVars.prms["dbgGeom"]: print("locList: ", geom.locList)
    
class routeGeom():
    def __init__(self):
        pass
    
    def initRoutes(self, geometry, guiDict):
        from fileProc import readFiles
        files = readFiles()
        print("\ninitializing route dicts: ")

        tmpRoute = files.readFile("routeFile")
        routeProto = tmpRoute.pop("routeProto")
        for item in guiDict:
            newRoute = {}
            if guiDict[item]["type"] != "route": continue
            
            routeName = item
            leftObj = guiDict[item]["leftObj"]
            rtObj = guiDict[item]["rtObj"]
            newRoute[routeName] = routeProto
            newRoute[routeName]["leftObj"] = leftObj
            newRoute[routeName]["rtObj"] = rtObj
            newRoute[routeName]["transTime"] = guiDict[item]["transTime"]
            newRoute[routeName]["trnLabelTag"] = routeName+"trnLblTag"
            newRoute[routeName]["trains"] = []

            # route lines are drawn west-to-east; train locs follow

            newRoute[routeName].update(self.routeLine(routeName, guiDict))
            newRoute[routeName].update(self.trnsOnRoutes(newRoute[routeName], routeName, guiDict))

            if mVars.prms["dbgGeom"]: print("\ninitRoutes: newRoute: ", newRoute)
            routeCls.routes[routeName] = dict(newRoute[routeName])
            if mVars.prms["dbgGeom"]: print("\nRoutes = ", routeCls.routes)
            
        for loc in geometry:
            if (loc == leftObj) or (loc == rtObj):
                rtList = geometry[loc].get("routes")
                rtList.append(routeName)
                geometry[loc]["routes"] = rtList
        if mVars.prms["dbgGeom"]: print("\ninitRoutes: geometry for loc: ", loc, "is", geometry[loc])
        #if mVars.prms["dbgGeom"]: print("\nnewRoutes: ", newRoute)
        return

    def trnsOnRoutes(self, routeDict, rtNam, guiDict):
        leftObj = guiDict[guiDict[rtNam]["leftObj"]]
        xDist, yDist, lineLen = self.rtGeomCalcs(rtNam, guiDict)
        yRoute = (leftObj["y0"] + leftObj["y1"])*0.5
        height = leftObj["y1"] - leftObj["y0"]
    
        #if mVars.prms["dbgGeom"]: print("trnsOnRoutes: trnrtLength: ", 
        #        trainParams.trnrtLength, "rtObj[x0]", rtObj["x0"])

        routeDictOut = {
            "yTrn": yRoute - height*0.25,
            "yTrnCon": leftObj["y0"] - 5,
            "rtLength": lineLen,
            "distPerTime": lineLen/routeDict["transTime"]
                    }
        return routeDictOut

    # routeLine draws lines to represent all routes between endpoints
    # no regard for direction, just want the lines between locs
    # train gui data is initialized in trnsOnRoutes
    def routeLine(self, rtNam, guiDict):
        coordObj = transForms()
        xDist, yDist, lineLen = self.rtGeomCalcs(rtNam, guiDict)
        leftObj = guiDict[guiDict[rtNam]["leftObj"]]
        rtObj = guiDict[guiDict[rtNam]["rtObj"]]
        y0 = (leftObj["y0"] + leftObj["y1"])*0.5
        y1 = (rtObj["y0"] + rtObj["y1"])*0.5
        
        routeDictOut = {
            "x0": leftObj["x1"],
            "x1": rtObj["x0"],
            "y0": y0,
            "y1": y1,
            "cosTh": round(xDist/lineLen, 3),
            "sinTh": round(yDist/lineLen, 3)
                  }
        
        return routeDictOut

    def rtGeomCalcs(self, rtNam, guiDict):        
        leftObj = guiDict[guiDict[rtNam]["leftObj"]]
        rtObj = guiDict[guiDict[rtNam]["rtObj"]]
        y0 = (leftObj["y0"] + leftObj["y1"])*0.5
        y1 = (rtObj["y0"] + rtObj["y1"])*0.5
        
        yDist = abs(y1 - y0)
        xDist = abs(rtObj["x0"] - leftObj["x1"])
        lineLen = math.sqrt(xDist*xDist+yDist*yDist)
            
        return xDist, yDist, lineLen

