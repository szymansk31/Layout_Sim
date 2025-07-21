import json
from fileNamesIO import fileNames


#=================================================
class readFiles():
    def __init__(self):
        #self.trainID = int
        pass
        
    def readFile(self, fileToRead):
        print("\nreading ", fileToRead)
        if "param" in fileToRead:
            fullFName = fileToRead
        else:
            fileObj = fileNames()
            fnames = fileObj.fNames
            fullFName = fnames[fileToRead]
        try: 
            jsonFile = open (fullFName, "r")
            inputDict = json.load(jsonFile)
            jsonFile.close()
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        #if mVars.prms["dbgFileRd"]: print("Dict Read: ", inputDict)
        print("Dict Read: ", inputDict)
        return inputDict

