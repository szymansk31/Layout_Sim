            
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

from layoutGeom import geom
layoutObj = geom()
geometry = mVars.geometry = files.readFile("layoutGeomFile")
layoutObj.locListInit(geometry)
mVars.routes = layoutObj.defRoutes(geometry)


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

from gui import gui, display
guiObj = gui()
guiDict = files.readFile("guiInfo.txt")
dispObj = display()
dispObj.drawLayout(guiDict)

idx = 0
count = 0
maxCount = 7
print("\n")
for loc in geometry:
    if mVars.prms["debugGeom"]: print("location: ", loc,": ", geometry[loc])
    idx +=1

#main loop:
print("mVars.time: ", mVars.time, "maxtime: ", mVars.prms["maxTime"])
while mVars.time < mVars.prms["maxTime"]:
    print("\nmVars.time: ", mVars.time)
    for train in trainDB.trains:
        currentLoc = trainDB.trains[train]["currentLoc"]
        if mVars.prms["dbgLoop"]: print ("Before train processing: train: ", 
            train, "currentLoc: ", currentLoc)
        trnProcObj.trainCalcs(trainDB.trains[train], train)
    count +=1

    if count == maxCount:
        if mVars.prms["dbgLoop"]: print("trainDict[",train,"] = ", trainDB.trains[train])
        currentLoc = trainDB.trains[train]["currentLoc"]
        if "route" not in currentLoc:
            print("\nloc[",currentLoc,"]", geometry[currentLoc])
        count = 0
    for loc in geometry:
        if mVars.prms["dbgLoop"]: print ("\nBefore loc processing: loop var loc: ", 
            loc, "currentLoc: ", currentLoc)

        ydProcObj.yardCalcs(geometry, loc)
    mVars.time +=1

gui.editWindow.mainloop()