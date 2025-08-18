
import matplotlib.pyplot as plt
import numpy as np
from mainVars import mVars
from stateVars import locs, trainDB, routeCls
from display import dispItems
from yardCalcs import ydCalcs
from swCalcs import swCalcs
from stagCalcs import stCalcs
from gui import gui
from coords import transForms
from dispatch import dspCh, rtCaps
from outputMethods import printMethods


class savTimSeries():
    
    def __init__(self):
        self.labels = ["time", "Location", "Destination", "# Cars", 
            "trains"]
        pass
    
    def readStatFilev1(self):
        statFile = "output/stats_08_16_at_2103.txt"
        varDict = {}
        with open (statFile, "r") as statFile:
            for line in statFile:
                clean_line = line.strip()
                print("clean_line: ", clean_line)
                if "time step" in line: 
                    parts = clean_line.split(" ")
                    #print(parts)
                    time = int(parts[2])
                    if time != varDict["time"]:
                        varDict["time"] = time
                if "Location" in line: 
                    parts = clean_line.split(" ")
                    #print(parts)
                    loc = parts[1]
                try:
                    print(time, ",", loc)
                except:
                    pass
                #skipLine = statFile.readline()
                
    def readStatFile(self):
        statFile = "output/stats_08_16_at_2103.txt"
        varDict = [{"time":0}]
        with open (statFile, "r") as statFile:
            for line in statFile:
                clean_line = line.strip("\n")
                #print("clean_line: ", clean_line)
                if "time step" in line: 
                    parts = clean_line.split(" ")
                    time = int(parts[2]) - 25
                    print("time: ", time, ", line: ", clean_line)
                    if time != varDict[time]["time"]:
                        varDict[time].update({"time": time})
                else:
                    for label in self.labels:
                        if label in line:
                            parts = clean_line.split(" ")
                            varDict[time].update({label: clean_line})
                    print(varDict)
            try:
                print(varDict)
            except:
                pass
                #skipLine = statFile.readline()
                
savObj = savTimSeries()
savObj.readStatFile()
