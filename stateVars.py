


#=================================================
class locs():
    locDat = {}
    
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
        stVarSaves.savLocs[saveNam] = locs.locDat     
        stVarSaves.savtrains[saveNam] = trainDB.trains       
        stVarSaves.savConsists[saveNam] = trainDB.consists
        stVarSaves.savYdTrains[saveNam] = trainDB.ydTrains
        stVarSaves.savRoutes[saveNam] = routeCls.routes
        
        if stVarSaves.savIDX == mVars.prms["maxSaves"] - 1:
            stVarSaves.savIDX = 0
            
        
    def restStVars(self, stepsBack):
        restNam = "save" + str(stVarSaves.savIDX - stepsBack)
        locs.locDat = stVarSaves.savLocs[restNam]
        trainDB.trains = stVarSaves.savtrains[restNam]
        trainDB.consists = stVarSaves.savConsists[restNam]
        trainDB.ydTrains = stVarSaves.savYdTrains[restNam]
        routeCls.routes = stVarSaves.savRoutes[restNam]



        