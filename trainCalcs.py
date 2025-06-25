import numpy as np
import json
from mainVars import mVars


#=================================================
class trainProc():
    numTrains = 0
    def __init__(self):
        #self.trainID = int
        pass
        
    def initTrain(files):
        print("\n creating train dictionary ", trainProc.numTrains)
        try: 
            jsonFile = open (files.trainDictFile, "r")
            trainDict = json.load(jsonFile)
            jsonFile.close()
            trainProc.numTrains +=1
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        print("trainDict: ", trainDict)
        print("adding initial consist")
        return trainDict

    def initConsist(files):
        print("\n creating train dictionary ", trainProc.numTrains)
        try: 
            jsonFile = open (files.consistFile, "r")
            consistDict = json.load(jsonFile)
            jsonFile.close()
            trainProc.numTrains +=1
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        print("consistDict: ", consistDict)
        return consistDict

        
    def trainCalcs(self, trainDict):
        match trainDict["status"]:
            case "enroute":
                variance = np.random.normal(loc=0, scale=0.25, size=1)
                timeEnRoute = trainDict["timeEnRoute"] + mVars.prms["timeStep"] + variance
                trainDict["timeEnRoute"] = timeEnRoute
                route = trainDict["currentLoc"]
                transTime = mVars.routes[trainDict["currentLoc"]]["transTime"]
                print("trainCalcs: train: ", trainDict["trainNum"], "route: ", route, 
                    ", transTime:", transTime, ", timeEnRoute: ", timeEnRoute,
                    ", variance: ", variance)
                if trainDict["timeEnRoute"] >= transTime:
                    trainDict["currentLoc"] = mVars.routes[trainDict["currentLoc"]]["dest"]
                    mVars.geometry[trainDict["currentLoc"]]["trains"].append(trainDict["trainNum"])
                    trainDict["status"] = "enterYard"
                    trainDict["timeEnRoute"] = 0
                    mVars.numOpBusy -=1
                    
            case "enterYard":
                pass
            case "leaving":
                pass
            case "switching":
                pass
