#--- No hit class - used to track icao codes webersrive not resolving to aviod later hits memory only
class noHit:
    "noHit ICAO DB "
    noHitID = ""
    noHitWhenSeen = ""
    noHitWhenSeenComputer = ""

    def __init__(self, aircraftID):
        self.noHitID = aircraftID

    def get_noHitID(self):
        return self.noHitID

    def set_noHitWhenSeen(self, aWhenSeen):
        self.noHitWhenSeen = aWhenSeen

    def get_noHitWhenSeen(self):
        return self.noHitWhenSeen

    def set_noHitWhenSeenComputer(self, aWhenSeenComputer):
        self.noHitWhenSeenComputer = aWhenSeenComputer

    def get_noHitWhenSeenComputer(self):
        return self.noHitWhenSeenComputer        
