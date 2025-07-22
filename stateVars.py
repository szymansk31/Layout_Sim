

import copy
import json

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



    def dumpJSON(self):
        spacer = "locs.locDat: \n\n\n"
        with open ("output/stVars.txt", "w") as jsonFile:
            json.dump(spacer, jsonFile)
            json.dump(locs.locDat, jsonFile)
            spacer = "trainDC.trains: \n\n\n"
            json.dump(spacer, jsonFile)
            json.dump(trainDB.trains, jsonFile)
            json.dump(trainDB.consists, jsonFile)
            json.dump(trainDB.ydTrains, jsonFile)
            json.dump(routeCls.routes, jsonFile)
        try:    
            "output/stVars.txt".close()
        except:
            print("\nCould not find stVars.txt")


        