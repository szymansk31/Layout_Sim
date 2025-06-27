import numpy as np
import json
from mainVars import mVars


#=================================================
class trainProc():
    numTrains = 0
    def __init__(self):
        #self.trainID = int
        pass
        
    def initTrain(self, files):
        print("\ncreating train dictionary ", trainProc.numTrains)
        try: 
            jsonFile = open (files.trainDictFile, "r")
            trainDict = json.load(jsonFile)
            jsonFile.close()
            trainProc.numTrains +=1
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        if mVars.prms.debugTrainDict: print("trainDict: ", trainDict)
        print("adding initial consist")
        consist = self.initConsist(files)
        mVars.consists.update(consist)
        trainDict["consistNum"] = consist["consistNum"]
        return trainDict

    def initConsist(self, files):
        print("\ncreating consist ")
        try: 
            jsonFile = open (files.consistFile, "r")
            consistDict = json.load(jsonFile)
            jsonFile.close()
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        consistDict["consistNum"] = mVars.numConsists
        mVars.numConsists +=1
        if mVars.prms.debugTrainDict: print("consistDict: ", consistDict)
        return consistDict

        
    def trainCalcs(self, trainDict):
        match trainDict["status"]:
            case "enroute":
                variance = np.random.normal(loc=0, scale=0.25, size=1)
                timeEnRoute = trainDict["timeEnRoute"] + mVars.prms["timeStep"] + variance
                trainDict["timeEnRoute"] = timeEnRoute
                route = trainDict["currentLoc"]
                transTime = mVars.routes[trainDict["currentLoc"]]["transTime"]
                if mVars.prms.debugTrainProc: print("trainCalcs: train: ", trainDict["trainNum"], "route: ", route, 
                    ", transTime:", transTime, ", timeEnRoute: ", timeEnRoute,
                    ", variance: ", variance)
                if trainDict["timeEnRoute"] >= transTime:
                    trainDict["currentLoc"] = mVars.routes[trainDict["currentLoc"]]["dest"]
                    mVars.geometry[trainDict["currentLoc"]]["trains"].append(trainDict["trainNum"])
                    if trainDict["currentLoc"] == trainDict["finalLoc"]:
                        trainDict["status"] = "terminate"
                    else: 
                        trainDict["status"] = "dropPickup"
                    trainDict["timeEnRoute"] = 0
                    mVars.numOpBusy -=1
                    
            case "building":
                pass
            case "terminate":
                pass
            case "dropPickup":
                if "sw" in trainDict["currentLoc"]:   
                    pass
                else: 
                    pass
                pass
            case "ready2Leave":
                trainDict["status"] = "enroute"
                pass
