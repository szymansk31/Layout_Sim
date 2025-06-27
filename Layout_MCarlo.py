            
#=================================================
class swAreaProc():
    yardName = str
    numTracks  = int
    numDest = int
    fracTrainBuild = int        #fraction of classified cars built into trains
    rateClassification = int    #num cars classified/time
    numAdjYards = int           #num adjacent yards
    adjYardNames = []
    time2AdjYards = []
    trainOut = int
    swAreaNames = []
    
    
    def __init__(self):
        pass
    
    def swAreaSetup(self):
        print("\nsetting up switching area ", self.swAreaNames)
        
        
    def swAreaCalcs(self):
        self.trainOut = self.rateClassification*self.fracTrainBuild/mVars.trainSize
    
            

#########################################################
# start of code
#########################################################

#def main():    
from fileProc import readFiles
files = readFiles()

from mainVars import mVars
mVars.prms = files.readFile("paramFile")

from layoutGeom import layoutGeom
layout = layoutGeom()
geometry = mVars.geometry = files.readFile("layoutGeomFile")
mVars.routes = layout.defRoutes(geometry)


#setup initial car distribution
from carProc import carProc
carProcObj = carProc()
carDict = files.readFile("carFile")
carProcObj.procCarFileInfo(carDict)

from locProc import locProc
ydProcObj = locProc()
from trainProc import trainProc, trainDB
trnProcObj = trainProc()
trains = trainDB()
trains.initTrain()

idx = 0
count = 0
maxCount = 7
print("\n")
for loc in geometry:
    if mVars.prms["debugGeom"]: print("location: ", loc, ", index: ", idx, ": ", geometry[loc])
    idx +=1

#main loop:
print("mVars.time: ", mVars.time, "maxtime: ", mVars.prms["maxTime"])
while mVars.time < mVars.prms["maxTime"]:
    for train in trainDB.trains:
        trnProcObj.trainCalcs(trainDB.trains[train])
    count +=1

    if count == maxCount:
        if mVars.prms["debugTrainProc"]: print("trainDict[",train,"] = ", trainDB.trains[train])
        currentLoc = trainDB.trains[train]["currentLoc"]
        if "route" not in currentLoc:
            print("\nloc[",currentLoc,"]", geometry[currentLoc])
        count = 0
    for loc in geometry:
        ydProcObj.yardCalcs(geometry, loc)
    mVars.time +=1
