import numpy as np
from mainVars import *
 
            
#=================================================
class layoutGeom():
    
    def __init__(self):
        pass
    
    def defRoutes(self, geometry):
        idx = 1
        routes = {}
        for loc in geometry:
            destIDX = 0
            for dest in geometry[loc]["adjLocNames"]:
                if mVars.prms["debugGeom"]: print("in defRoutes; orig, dest: ", loc, ",", dest)
                transTime = geometry[loc]["time2AdjLocs"][destIDX]
                routeName = "route"+str(idx)
                routes[routeName] = {"origin": loc, "dest": dest, "transTime": transTime}
                rtList = geometry[loc].get("routes")
                rtList.append(idx)
                geometry[loc]["routes"] = rtList
                if mVars.prms["debugGeom"]: print("\ndefRoutes: geometry for loc: ", loc, "is", geometry[loc])
                destIDX +=1
                idx +=1
        if mVars.prms["debugGeom"]: print("\nroutes: ", routes)
        return routes

     
