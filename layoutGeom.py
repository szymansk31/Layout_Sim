import numpy as np
from mainVars import *
 
            
#=================================================
class geom():
    layoutLocsRoutes = {}
    locList = []

    def __init__(self):
        pass
    
    def locListInit(self, geometry):
        for loc in geometry:
            geom.locList.append(loc)
        if mVars.prms["debugGeom"]: print("locList: ", geom.locList)
    
    def initRoutes(self, geometry, guiDict):
        idx = 1
        routes = {}
        for loc in geometry:
            destIDX = 0
            for dest in geometry[loc]["adjLocNames"]:
                if mVars.prms["debugGeom"]: print("in initRoutes; orig, dest: ", loc, ",", dest)
                transTime = geometry[loc]["time2AdjLocs"][destIDX]
                routeName = "route"+str(idx)
                routes[routeName] = {"origin": loc, "dest": dest, "transTime": transTime}
                if idx < 3:
                    routes[routeName].update(self.routeLine(routes[routeName], routeName, guiDict))
                if mVars.prms["debugGeom"]: print("\ninitRoutes: route[",routeName,"] = ", routes[routeName])
                rtList = geometry[loc].get("routes")
                rtList.append(idx)
                geometry[loc]["routes"] = rtList
                if mVars.prms["debugGeom"]: print("\ndefRoutes: geometry for loc: ", loc, "is", geometry[loc])
                destIDX +=1
                idx +=1
        if mVars.prms["debugGeom"]: print("\nroutes: ", routes)
        return routes

    def routeLine(self, routeDict, rtNam, guiDict):
        leftObj = guiDict[guiDict[rtNam]["leftObj"]]
        rtObj = guiDict[guiDict[rtNam]["rtObj"]]
        yLoc = (leftObj["y0"] + leftObj["y1"])*0.5
        height = leftObj["y1"] - leftObj["y0"]
        distance = rtObj["x0"] - leftObj["x1"]
        xTrnTxt = (leftObj["x1"] + rtObj["x0"])*0.5
        routeDict = {
            "x0": leftObj["x1"],
            "x1": rtObj["x0"],
            "y0": yLoc,
            "y1": yLoc,
            "xTrnInit": leftObj["x1"],
            "yTrn": yLoc - height*0.25,
            "trnWid": 20,
            "trnHt": 10,
            "xTrnTxt": xTrnTxt,
            "yTrnTxt": leftObj["y0"] - 20,
            "yTrnCon": leftObj["y0"] - 5,
            "distPerTime": distance/routeDict["transTime"]
                    }
        return routeDict

