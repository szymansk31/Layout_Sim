    def buildNewTrain_old(self, loc):
        from trainProc import trainInit

        numCars, maxCarTrk = self.ready2Build(loc)
        if numCars != 0:            
            trainObj = trainInit()
            trnName, conName = trainObj.newTrain()
            
            nextLoc, numstops, stops = self.setStops(loc, maxCarTrk)
            print("train: ", trnName, ", stops: ", stops)
            trainDB.trains[trnName].update( {
                "status": "building",
                "origLoc": loc,
                "nextLoc": nextLoc,
                "currentLoc": loc,
                "finalLoc": maxCarTrk,
                "numStops": numstops,
                "departStop": loc,
                "stops": stops,
                "color": trainInit.colors()           
                    })
            # consist gets stops that have cars to drop, not those where
            # the train continues through.  Pickups are triggered by
            # "dropPickup" status in that location and will add to consists
            trainDB.consists[conName].update({
                "stops": {maxCarTrk:{"box": 0, "tank": 0,"rfr": 0, "hop": 0, 
                "gons": 0, "flats": 0}  }
            })
            
            print("new train: ", trnName, ": ", trainDB.trains[trnName])
            print("new consist: ", conName, ":", trainDB.consists[conName])
            trainDB.ydTrains["buildTrain"].append(trnName)
            locs.locDat[loc]["trains"].append(trnName)
            return

    
