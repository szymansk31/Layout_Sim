

import copy

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
    savLocs     =   {}
    savtrains   =   {}
    savConsists =   {}
    savYdTrains =   {}
    savRoutes   =   {}
    savIDX    =   0
    
    def __init__(self):

        pass
    
    def saveStVars(self):
        saveNam = "save" + str(stVarSaves.savIDX)
        stVarSaves.savLocs[saveNam] = copy.deepcopy(locs.locDat)     
        stVarSaves.savtrains[saveNam] = copy.deepcopy(trainDB.trains)       
        stVarSaves.savConsists[saveNam] = copy.deepcopy(trainDB.consists)
        stVarSaves.savYdTrains[saveNam] = copy.deepcopy(trainDB.ydTrains)
        stVarSaves.savRoutes[saveNam] = copy.deepcopy(routeCls.routes)
        
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
        locs.locDat = copy.deepcopy(stVarSaves.savLocs[restNam])
        trainDB.trains = copy.deepcopy(stVarSaves.savtrains[restNam])
        trainDB.consists = copy.deepcopy(stVarSaves.savConsists[restNam])
        trainDB.ydTrains = copy.deepcopy(stVarSaves.savYdTrains[restNam])
        routeCls.routes = copy.deepcopy(stVarSaves.savRoutes[restNam])



        