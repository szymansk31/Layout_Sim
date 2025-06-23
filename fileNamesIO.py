import json

defParamDictFile = "paramDict.txt"
defTrainDictFile = "trainDict.txt"
defLayoutGeomFile = "layoutGeom.txt"

#=================================================
class fileNames:
    def __init__(self):
        self.paramDictFile = defParamDictFile
        self.trainDictFile = defTrainDictFile
        self.layoutGeomFile = defLayoutGeomFile


#=================================================
class readFiles:

    def __init__(self, files):
        self.files = files      
    
