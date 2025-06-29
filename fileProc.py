import json
from mainVars import mVars
from fileNamesIO import fileNames


#=================================================
class readFiles():
    def __init__(self):
        #self.trainID = int
        pass
        
    def readFile(self, fileToRead):
        fileObj = fileNames()
        fnames = fileObj.fNames
        print("\nreading ", fileToRead)
        try: 
            jsonFile = open (fnames[fileToRead], "r")
            inputDict = json.load(jsonFile)
            jsonFile.close()
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        #if mVars.prms["dbgFileRd"]: print("Dict Read: ", inputDict)
        print("Dict Read: ", inputDict)
        return inputDict

