
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from routeProc import rtCaps
from datetime import datetime
import json

class printMethods():
    
    def __init__(self):
        self.rtCapsObj =rtCaps() 
        pass

    def printTrainInfo(self, trainNam):
        trainStem = trainDB.trains[trainNam]
        numCars = trainStem["numCars"]
        currentLoc = trainStem["currentLoc"]
        nextLoc = trainStem["nextLoc"]
        finalLoc = trainStem["finalLoc"]
        origLoc = trainStem["origLoc"]
        status = trainStem["status"]
        direction = trainStem["direction"]
        if mVars.prms["dbgLoop"]: print (
            "Before proc: ", trainNam, ", #cars: ", numCars,
            "currL: ", currentLoc, ", nextL: ", nextLoc, 
            ", origL: ", origLoc, 
            ", finL: ", finalLoc, ", dir: ", direction,
            "status: ", status)

    def writeTrainInfo(self, file, trainNam):
        trainStem = trainDB.trains[trainNam]
        numCars = trainStem["numCars"]
        currentLoc = trainStem["currentLoc"]
        nextLoc = trainStem["nextLoc"]
        finalLoc = trainStem["finalLoc"]
        origLoc = trainStem["origLoc"]
        status = trainStem["status"]
        direction = trainStem["direction"]
        if mVars.prms["dbgLoop"]: 
            file.write (
            "\nStart of main loop: " + trainNam + ", #cars: " + str(numCars) + 
            ", currL: " + currentLoc + ", nextL: " + nextLoc + 
            ", origL: " + origLoc + 
            ", finL: " + finalLoc + ", dir: " + direction + 
            ", status: " + status)

    def writeRtCaps(self, file, routeNam):
        file.write("\nroute capacities: ")
        file.write("\n" + routeNam + ": " +  \
            "trains: " + str(routeCls.routes[routeNam]["trains"]) + \
            str(routeCls.routes[routeNam]["capacity"]))
       
class statSave():
    statFile  = ""
    timeFile  = ""
    timeSeries = {}

    def __init__(self):
        self.printObj = printMethods()
        pass

    def savStats(self):
        now = datetime.now()
        date_time = now.strftime("%m_%d_at_%H%M")
        fileName = "output/stats_" + date_time + ".txt"
        statSave.statFile = fileName
        with open (fileName, "a") as statFile:
            statFile.write("\n\n===============================")
            statFile.write("===============================\n")
            statFile.write("Time step: " + str(mVars.time))
            for loc in locs.locDat:
                statFile.write("\n---------------------------")
                statFile.write("\ntime step: " + str(mVars.time))
                statFile.write("\nLocation: " + loc)
                statFile.write("\nDestination, #cars:    ")
                locStem = locs.locDat[loc]
                for dest in locStem["destTrkTots"]:
                    numCars = locStem["destTrkTots"][dest]
                    statFile.write(dest + "  " + str(numCars) + "  ")
                text = "\n# Cars: " + str(locStem["totCars"])
                if locStem["type"] != "staging":
                    text +=  ", class: " + str(locStem["cars2Class"])
                statFile.write(text)
                text = "\ntrains built: " + str(locStem["trnCnts"]["built"]) +\
                    "; started: " + str(locStem["trnCnts"]["started"]) +\
                    "; switched: " + str(locStem["trnCnts"]["switched"]) +\
                    "; brkDown: " + str(locStem["trnCnts"]["brkDown"]) +\
                    "; continue: " + str(locStem["trnCnts"]["continue"])
                statFile.write(text)
 
                statFile.write("\nTrain and consist:     ")

                for train in locStem["trains"]:
                    self.printObj.writeTrainInfo(statFile, train)
                    consistNum = trainDB.trains[train]["consistNum"]
                    consistNam = "consist"+str(consistNum)
                    stopStem = trainDB.consists[consistNam]["stops"]
                    statFile.write("\n" + train + " stops:")
                    trnStopStem = trainDB.trains[train]["stops"]
                    for stop in trnStopStem:
                        statFile.write("\n"+ stop \
                             + str(trnStopStem[stop]))
                    for stop in stopStem:
                        numCars = sum(stopStem[stop].values())
                        statFile.write("\n"+ stop +": #cars: "+\
                            str(numCars) + str(stopStem[stop]))
                    statFile.write("\n")

            for routeNam in routeCls.routes:
                statFile.write("\n---------------------------\n")
                statFile.write("\ntime step: " + str(mVars.time))
                statFile.write("\nroute: " + routeNam)
                self.printObj.writeRtCaps(statFile, routeNam)
                statFile.write("\nTrain and consist:     ")
                for train in routeCls.routes[routeNam]["trains"]:
                    self.printObj.writeTrainInfo(statFile, train)
                    consistNum = trainDB.trains[train]["consistNum"]
                    consistNam = "consist"+str(consistNum)
                    stopStem = trainDB.consists[consistNam]["stops"]
                    statFile.write("\n" + train + " stops:")
                    for stop in stopStem:
                        statFile.write("\n" + stop + ": " + str(stopStem[stop]))
                    statFile.write("\n")
            statFile.flush()

    def timeSeries(self):
        now = datetime.now()
        date_time = now.strftime("%m_%d_at_%H%M")
        fileName = "output/timeSeries_" + date_time + ".txt"
        statSave.timeFile = fileName
        timeKey = "time" + str(mVars.time)
        varDict = {}
        varDict[timeKey] = {}
        with open (fileName, "a") as timeFile:
            for loc in locs.locDat:
                tmpDict = {}
                locStem = locs.locDat[loc]
                carCountDict = {"nCars": locStem["totCars"]}
                if locStem["type"] != "staging":
                    carCountDict["class"] = locStem["cars2Class"]
                tmpDict.update(carCountDict)
                destDict = {}
                for dest in locStem["destTrkTots"]:
                    numCars = locStem["destTrkTots"][dest]
                    destDict.update({dest: numCars})
                tmpDict.update(destDict)
                trnCnts = {"built":  locStem["trnCnts"]["built"],
                    "started":  locStem["trnCnts"]["started"],
                    "switched":  locStem["trnCnts"]["switched"],
                    "brkDown":  locStem["trnCnts"]["brkDown"],
                    "continue":  locStem["trnCnts"]["continue"]}
                tmpDict.update(trnCnts)
                varDict[timeKey][loc] = tmpDict

            #timeFile.write("{")
            if timeKey != "time0": timeFile.write(",")
            timeFile.write("\n" + str(varDict))
            #json.dump(varDict, timeFile)
"""
            for route in routeCls.routes:
                timeFile.write("\n---------------------------\n")
                timeFile.write("\ntime step: " + str(mVars.time))
                timeFile.write("\nroute: " + route)
                self.printObj.writeRtCaps(timeFile, route)
                timeFile.write("\nTrain and consist:     ")
                for train in routeCls.routes[route]["trains"]:
                    self.printObj.writeTrainInfo(timeFile, train)
                    consistNum = trainDB.trains[train]["consistNum"]
                    consistNam = "consist"+str(consistNum)
                    stopStem = trainDB.consists[consistNam]["stops"]
                    timeFile.write("\n" + train + " stops:")
                    for stop in stopStem:
                        timeFile.write("\n" + stop + ": " + str(stopStem[stop]))
                    timeFile.write("\n")
            timeFile.flush()
"""
