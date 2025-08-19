

import copy
import json

#=================================================
class dspCh():
    dspchDat = {}
    sched = {}
    
    pass
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
    strtTrns = []
    
    def __init__(self):
        pass
    
    def getConNam(train):
        consistNum = trainDB.trains[train]["consistNum"]
        consistNam = "consist"+str(consistNum)
        return consistNam


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


