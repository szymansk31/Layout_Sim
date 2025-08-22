
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
        filename = "output/timeSeries_08_20_at_2027.txt"
        with open (filename, "r") as inFile:
            for line in inFile: 
                if line != "\n":
                    tmpDict = ast.literal_eval(line)
                    if isinstance(tmpDict, tuple): tmpDict = tmpDict[0]
                    timeKey = next(iter(tmpDict))
                    print("timeKey: ", timeKey)
                    self.timeSrsDict[timeKey] = tmpDict.pop(timeKey)
                    #print("next line in dict: ", self.timeSrsDict)

        #print("input dict: ", self.timeSrsDict)

    def plotTimeSeries(self):
        timeList = []
        nCars = {}
        nCarsPgh = []
        nCarsKiski = []
        legend = []
        for loc in self.timeSrsDict["time0"]:
            nCars[loc] = []
            legend.append(loc)
        print("nCars: ", nCars)
        for time in self.timeSrsDict:
            
            timeList.append(time[4:])
            nCarsPgh.append(self.timeSrsDict[time]["pgh"]["nCars"])
            nCarsKiski.append(self.timeSrsDict[time]["Kiski"]["nCars"])
            for loc in self.timeSrsDict[time]:
                nCars[loc]
                nCars[loc].append(self.timeSrsDict[time][loc]["nCars"])
            #plt.plot(time, thr, color='k')  
            #plt.plot(time, drawBar/2000, color='b')
            #plt.plot(time, mph, color='r')
        plt.figure(figsize=[8,4])
        plt.plot(timeList, nCarsPgh, color='g')  
        plt.plot(timeList, nCarsKiski, color='r')  
        plt.show(block=False)
        
        plt.figure(figsize=[8,4])
        for loc in nCars:
            plt.plot(timeList, nCars[loc])
        plt.legend(legend,loc='lower left')
        plt.xticks(np.arange(0, 80, 5))
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



