import json

defParamDictFile = "paramDict.txt"
defTrainDictFile = "trainDict.txt"
defLayoutGeomFile = "layoutGeom.txt"
defCarDictFile    = "initCarDict.txt"

#=================================================
class fileNames:
    
    def __init__(self):
        #self.files = fileNames()
        self.paramDictFile = defParamDictFile
        self.trainDictFile = defTrainDictFile
        self.layoutGeomFile = defLayoutGeomFile
        self.carDictFile = defCarDictFile


#=================================================
class readFiles:

    def __init__(self, files):
        self.files = files      
    
