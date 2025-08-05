import random
import numpy as np
from mainVars import mVars
from stateVars import locs, dspCh, trainDB, routeCls
from display import dispItems
from yardCalcs import ydCalcs
from swCalcs import swCalcs
from stagCalcs import stCalcs
from gui import gui
from fileProc import readFiles

np.set_printoptions(precision=2, suppress=True) 


dbgLocal = 1   
  
#=================================================
class dspchProc():
    
    def __init__(self):
        pass
    
    def initDspchDicts(self):
        files = readFiles()
        print("initializing dispatch dicts: ")
        dspCh.dspchDat = files.readFile("dspchDatFile")

        # map dspchDat onto loc dicts for common data
        for loc in dspCh.dspchDat:
            dspCh.dspchDat["totCars"] = locs.locDat[loc]["totCars"]
            dspCh.dspchDat["numAdjLocs"] = locs.locDat[loc]["numAdjLocs"]
            dspCh.dspchDat["adjLocNames"] = locs.locDat[loc]["adjLocNames"]
            dspCh.dspchDat["trains"] = locs.locDat[loc]["trains"]
            dspCh.dspchDat["bldTrnDepTimes"] = locs.locDat[loc]["bldTrnDepTimes"]
            
