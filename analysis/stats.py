
import matplotlib.pyplot as plt
import numpy as np
import sys
import ast



class analyTimeSeries():
    
    def __init__(self):
        self.labels = ["time", "Location", "Destination", "# Cars", 
            "trains"]
        self.timeSrsDict = {}
        pass
    
    def readTimeSeries(self):
        #filename = sys.argv[1]
        filename = "output/timeSeries_08_18_at_2000.txt"
        with open (filename, "r") as inFile:
            for line in inFile: 
                print("input line: ", line)
                if line != "\n":
                    tmpDict = ast.literal_eval(line)
                    timeKey = next(iter(tmpDict))
                    print("timeKey: ", timeKey)
                    self.timeSrsDict[timeKey] = tmpDict
                    print("next line in dict: ", self.timeSrsDict)

        #print("input dict: ", self.timeSrsDict)

    def plotTimeSeries(self):
        timeList = []
        nCarsPgh = []
        for time in self.timeSrsDict:
            
            timeList.append(time)
            nCarsPgh.append(self.timeSrsDict[time]["pgh"]["nCars"])
            #plt.plot(time, thr, color='k')  
            #plt.plot(time, drawBar/2000, color='b')
            #plt.plot(time, mph, color='r')
            #plt.legend(["Cutoff", "Throttle", "Drawbar", "mph"])
        plt.figure()
        plt.bar(timeList, nCarsPgh, color='g')  
        plt.show(block=False)
        plt.show()

        
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
                
analyObj = analyTimeSeries()
analyObj.readTimeSeries()
analyObj.plotTimeSeries()



