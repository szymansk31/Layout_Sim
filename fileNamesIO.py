

#=================================================
class fileNames:
    
    def __init__(self):
        from mainVars import mVars
        self.fNames = {
            "paramFile": "paramDict.txt",
            "guiFile": mVars.prms["dictDirect"] + "/guiInfo.txt",
            #"layoutGeomFile": mVars.prms["dictDirect"] + "/layoutGeom.txt",
            "routeFile": mVars.prms["dictDirect"] + "/routeDict.txt",
            "scheduleFile": mVars.prms["dictDirect"] + "/schedule.txt",
            "locationFile": mVars.prms["dictDirect"] + "/locInfo.txt",
            "routeProtoFile": mVars.prms["dictDirect"] + "/routeProtoDict.txt",
            "trainFile": mVars.prms["dictDirect"] + "/trainDict.txt",
            "carFile": mVars.prms["dictDirect"] + "/initCarDict.txt",
            "consistFile": mVars.prms["dictDirect"] + "/consist.txt",
            "startingTrainFile": mVars.prms["dictDirect"] + "/startingTrains.txt",
            "startingConsistFile": mVars.prms["dictDirect"] + "/startingConsists.txt",
            "bare_consist_file": mVars.prms["dictDirect"] + "/bare_consist.txt"
            }


#=================================================
    
