import numpy as np
from mainVars import *
            
#=================================================
class carProc():
    
    def __init__(self):
        pass
    
    def readCarInitInfo(self, files):
        print("\nReading initial car info from file: ", files.carDictFile)
        try: 
            jsonFile = open (files.carDictFile, "r")
            carDict = json.load(jsonFile)
            jsonFile.close()
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        print("carDict: ", carDict)
        return carDict
    
    def procCarFileInfo(self, carDict):
        for loc in mVars.geometry:
            for carType in mVars.carTypes:
                for nextLoc in mVars.geometry:
                    carDict[loc][carType]["nextDest"].update({nextLoc: 0})
                print("carDict for carType: ", carType, ": ", carDict[loc][carType])
                
    def defRoutes(self, geometry):
        idx = 1
        routes = {}
        for loc in geometry:
            destIDX = 0
            for dest in geometry[loc]["adjLocNames"]:
                print("in defRoutes; orig, dest: ", loc, ",", dest)
                transTime = geometry[loc]["time2AdjLocs"][destIDX]
                routeName = "route"+str(idx)
                routes[routeName] = {"origin": loc, "dest": dest, "transTime": transTime}
                rtList = geometry[loc].get("routes")
                rtList.append(idx)
                geometry[loc]["routes"] = rtList
                print("\ndefRoutes: geometry for loc: ", loc, "is", geometry[loc])
                destIDX +=1
                idx +=1
        print("\nroutes: ", routes)
        return routes

     
