import numpy as np
from mainVars import *
 
            
#=================================================
class layoutGeom():
    
    def __init__(self):
        pass
    
    def readLayoutGeom(self, files):
        print("\nsetting up layout geometry", files.layoutGeomFile)
        try: 
            jsonFile = open (files.layoutGeomFile, "r")
            geometry = json.load(jsonFile)
            jsonFile.close()
        except FileNotFoundError:
            print("\njson file does not exist; returning")
            return
        print("geometry: ", geometry)
        return geometry

     
