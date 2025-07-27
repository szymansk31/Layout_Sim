

#=================================================
class fileNames:
    
    def __init__(self):
        from mainVars import mVars
        self.fNames = {
            "paramFile": "paramDict.txt",
            "guiFile": mVars.prms["dictDirect"] + "/guiInfo.txt",
            "layoutGeomFile": mVars.prms["dictDirect"] + "/layoutGeom.txt",
            "locationFile": mVars.prms["dictDirect"] + "/locInfoSwArea.txt",
            "routeFile": mVars.prms["dictDirect"] + "/routeDict.txt",
            "trainFile": mVars.prms["dictDirect"] + "/trainDict.txt",
            "carFile": mVars.prms["dictDirect"] + "/initCarDict.txt",
            "consistFile": mVars.prms["dictDirect"] + "/consist.txt",
            "startingTrainFile": mVars.prms["dictDirect"] + "/startingTrainsSwArea.txt",
            "startingConsistFile": mVars.prms["dictDirect"] + "/startingConsistsSwArea.txt",
            "bare_consist_file": mVars.prms["dictDirect"] + "/bare_consist.txt"
            }


#=================================================
    
