

import copy
import json
from datetime import datetime

#=================================================
class locs():
    locDat = {}
    locPop = {}
    labels= {}
    
#=================================================
class trainDB():
    numTrains = 5
    numConsists = 15

    trains = {}
    consists = {}
    ydTrains = {}

class routeCls():
    routes = {}

from mainVars import mVars
  
class stVarSaves():
    savlocdat   =   {}
    savtrains   =   {}
    savconsists =   {}
    savydtrains =   {}
    savroutes   =   {}
    savIDX    =   0
    
    def __init__(self):
        self.savNames = {
            "locDat": {
                "title": "\nlocation: ",
                "data": {}
                },
            "trains": {
                "title": "\ntrain: ",
                "data": {}
                },
            "consists": {
                "title": "\nconsist: ",
                "data": {}
                },
            "ydTrains": {
                "title": "\nydTrain: ",
                "data": {}
                },
            "routes": {
                "title": "\nroute: ",
                "data": {}
                }
        }
        from outputMethods import printMethods
        self.printObj = printMethods()

    
    def saveStVars(self):
        saveNam = "save" + str(stVarSaves.savIDX)
        stVarSaves.savlocdat[saveNam] = copy.deepcopy(locs.locDat)     
        stVarSaves.savtrains[saveNam] = copy.deepcopy(trainDB.trains)       
        stVarSaves.savconsists[saveNam] = copy.deepcopy(trainDB.consists)
        stVarSaves.savydtrains[saveNam] = copy.deepcopy(trainDB.ydTrains)
        stVarSaves.savroutes[saveNam] = copy.deepcopy(routeCls.routes)
        
    def incSavIDX(self):
        if stVarSaves.savIDX == mVars.prms["maxSaves"] - 1:
            stVarSaves.savIDX = 0
        else:
            stVarSaves.savIDX +=1
            
        
    def restStVars(self, stepsBack):
        # index set back by two, as savIDX incremented after dicts saved
        restIDX = stVarSaves.savIDX - stepsBack
        if restIDX < 0: restIDX += mVars.prms["maxSaves"]
        print("restStVars: old stVarSaves.IDX: ", stVarSaves.savIDX, "restIDX: ", 
              restIDX)
        stVarSaves.savIDX = restIDX
        restNam = "save" + str(restIDX)
        print("new stVarSaves.savIDX: ", stVarSaves.savIDX, "restNam: ", restNam)
        locs.locDat = copy.deepcopy(stVarSaves.savlocdat[restNam])
        trainDB.trains = copy.deepcopy(stVarSaves.savtrains[restNam])
        trainDB.consists = copy.deepcopy(stVarSaves.savconsists[restNam])
        trainDB.ydTrains = copy.deepcopy(stVarSaves.savydtrains[restNam])
        routeCls.routes = copy.deepcopy(stVarSaves.savroutes[restNam])

    def dumpStVars(self):
        with open ("output/stVars.txt", "w") as outFile:
            self.savNames["locDat"]["data"] = locs.locDat
            self.savNames["trains"]["data"] = trainDB.trains
            self.savNames["consists"]["data"] = trainDB.consists
            self.savNames["ydTrains"]["data"] = trainDB.ydTrains
            self.savNames["routes"]["data"] = routeCls.routes

            for item in self.savNames:
                savStem = self.savNames[item]
                outFile.write("\n\n================================\n")
                outFile.write(item+"\n")
                for subItem in savStem["data"]:
                    outFile.write(savStem["title"] + subItem + "\n")
                    outFile.write(str(savStem["data"][subItem]))


    def savStats(self):

        now = datetime.now()
        date_time = now.strftime("%m_%d_at_%H%M")
        fileName = "output/stats_" + date_time + ".txt"
        with open (fileName, "a") as statFile:
            statFile.write("\n\n===============================")
            statFile.write("===============================\n")
            statFile.write("time step: " + str(mVars.time))
            for loc in locs.locDat:
                statFile.write("\n\n---------------------------")
                statFile.write("\nLocation: " + loc)
                statFile.write("\nDestination, #cars     \n")

                for dest in locs.locDat[loc]["trackTots"]:
                    numCars = locs.locDat[loc]["trackTots"][dest]
                    statFile.write("  " + dest + "    " + str(numCars))
                statFile.write("\nTrain and consist:     ")

                for train in locs.locDat[loc]["trains"]:
                    self.printObj.writeTrainInfo(statFile, train)
                    consistNum = trainDB.trains[train]["consistNum"]
                    consistNam = "consist"+str(consistNum)
                    stopStem = trainDB.consists[consistNam]["stops"]
                    statFile.write("\n" + train + ":")
                    for stop in stopStem:
                        numCars = sum(stopStem[stop].values())
                        statFile.write("\n"+ stop +": #cars: "+\
                            str(numCars) + str(stopStem[stop]))

            for route in routeCls.routes:
                statFile.write("\n\n---------------------------\n")
                statFile.write("\nroute: " + route)
                statFile.write("\nTrain and consist:     ")
                for train in routeCls.routes[route]["trains"]:
                    self.printObj.writeTrainInfo(statFile, train)
                    consistNum = trainDB.trains[train]["consistNum"]
                    consistNam = "consist"+str(consistNum)
                    stopStem = trainDB.consists[consistNam]["stops"]
                    statFile.write("\n" + train + ":")
                    for stop in stopStem:
                        statFile.write("\n" + stop + ": " + str(stopStem[stop]))

        