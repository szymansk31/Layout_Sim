import numpy as np
from mainVars import *
 
            
#=================================================
class setupGeometry():
    
    def __init__(self):
        yardName = str
        numTracks  = int
        numDest = int
        fracTrainBuild = int        #fraction of classified cars built into trains
        rateClassification = int    #num cars classified/time
        numAdjYards = int           #num adjacent yards
        adjYardNames = []
        time2AdjYards = []
        trainOut = int

    
    def yardSetup(self):
        print("\nsetting up yard ", self.yardName)
        
        
    def yardCalcs(self):
        self.trainOut = self.rateClassification*self.fracTrainBuild/mainVar.trainSize
    
