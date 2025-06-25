import json

defParamDictFile = "paramDict.txt"
defTrainDictFile = "trainDict.txt"
defLayoutGeomFile = "layoutGeom.txt"
defCarDictFile    = "initCarDict.txt"
defLocInfoFile    = "locationInfo.txt"
defConsistFile    = "consist.txt"

#=================================================
class fileNames:
    
    def __init__(self):
        #self.files = fileNames()
        self.paramDictFile = defParamDictFile
        self.trainDictFile = defTrainDictFile
        self.layoutGeomFile = defLayoutGeomFile
        self.carDictFile = defCarDictFile
        self.locInfoFile = defLocInfoFile
        self.consistFile = defConsistFile


#=================================================
class readFiles:

    def __init__(self, files):
        self.files = files      
    
