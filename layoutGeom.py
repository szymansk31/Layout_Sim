from mainVars import *
from trainProc import trainParams
from gui import gui    

            
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
        idx = 1
        newRoute = {}
        from fileProc import readFiles
        files = readFiles()
        print("\ninitializing route dicts: ")

        for loc in geometry:
            destIDX = 0
            for dest in geometry[loc]["adjLocNames"]:
                if mVars.prms["dbgGeom"]: print("in initRoutes; orig, dest: ", loc, ",", dest)
                transTime = geometry[loc]["time2AdjLocs"][destIDX]
                routeName = "route"+str(idx)
                
                if gui.guiDict[loc]["x0"] > gui.guiDict[dest]["x0"]: 
                    rtObj = loc
                    leftObj = dest
                else: 
                    rtObj = dest
                    leftObj = loc
                    
                tmpRoute = files.readFile("routeFile")
     
                newRoute[routeName] = tmpRoute.pop("routeProto")
                newRoute[routeName]["leftObj"] = leftObj
                newRoute[routeName]["rtObj"] = rtObj
                newRoute[routeName]["transTime"] = transTime
                newRoute[routeName]["trnLabelTag"] = routeName+"trnLblTag"
                newRoute[routeName]["trains"] = []

                # route lines are drawn west-to-east; train locs follow

                newRoute[routeName].update(self.routeLine(newRoute[routeName], routeName, guiDict))
                newRoute[routeName].update(self.trnsOnRoutes(newRoute[routeName], routeName, guiDict))

                if mVars.prms["dbgGeom"]: print("\ninitRoutes: route[",routeName,"] = ", newRoute[routeName])
                rtList = geometry[loc].get("routes")
                rtList.append(routeName)
                geometry[loc]["routes"] = rtList
                if mVars.prms["dbgGeom"]: print("\ninitRoutes: geometry for loc: ", loc, "is", geometry[loc])
                destIDX +=1
                idx +=1
        if mVars.prms["dbgGeom"]: print("\nnewRoutes: ", newRoute)
        return newRoute

    def trnsOnRoutes(self, routeDict, rtNam, guiDict):
        leftObj = guiDict[guiDict[rtNam]["leftObj"]]
        rtObj = guiDict[guiDict[rtNam]["rtObj"]]
        yLoc = (leftObj["y0"] + leftObj["y1"])*0.5
        height = leftObj["y1"] - leftObj["y0"]
        distance = rtObj["x0"] - leftObj["x1"]
        xTrnTxt = (leftObj["x1"] + rtObj["x0"])*0.5
    
        #if mVars.prms["dbgGeom"]: print("trnsOnRoutes: trnLength: ", 
        #        trainParams.trnLength, "rtObj[x0]", rtObj["x0"])

        routeDictOut = {
            "yTrn": yLoc - height*0.25,
            "xTrnTxt": xTrnTxt,
            "yTrnTxt": leftObj["y0"] - 20,
            "yTrnCon": leftObj["y0"] - 5,
            "distPerTime": distance/routeDict["transTime"]
                    }
        return routeDictOut

    # routeLine draws lines to represent all routes between endpoints
    # no regard for direction, just want the lines between locs
    # train gui data is initialized in trnsOnRoutes
    def routeLine(self, routeDict, rtNam, guiDict):
        leftObj = guiDict[guiDict[rtNam]["leftObj"]]
        rtObj = guiDict[guiDict[rtNam]["rtObj"]]
        yLoc = (leftObj["y0"] + leftObj["y1"])*0.5
        routeDictOut = {
            "x0": leftObj["x1"],
            "x1": rtObj["x0"],
            "y0": yLoc,
            "y1": yLoc,
                    }
        return routeDictOut


