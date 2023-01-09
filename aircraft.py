###---- this is what we track aircraft in during runtime in memory 
class Aircraft:
    "Aircraft Class"
    aircraftID = ""
    aircraftOwner = "" 
    aircraftOperatorFlagCode = ""
    aircraftRegistration = ""
    aircraftType = ""
    aircraftWhenSeen = ""
    aircraftWhenSeenComputer = ""
    AlertTime = ""

    def __init__(self, aircraftID):
        self.aircraftID = aircraftID

    def get_aircraftID(self):
        return self.aircraftID

    def set_Owner(self, aOwner):
        self.aircraftOwner = aOwner

    def get_Owner(self):
        return self.aircraftOwner    
    
    def set_OperatorFlagCode(self, aOperatorFlagCode):
        self.aircraftOperatorFlagCode = aOperatorFlagCode   

    def get_OperatorFlagCode(self):
        return self.aircraftOperatorFlagCode 

    def set_Registration(self, aRegistration):
        self.aircraftRegistration = aRegistration

    def get_Registration(self):
        return self.aircraftRegistration

    def set_Type(self, aType):
        self.aircraftType = aType

    def get_Type(self):
        return self.aircraftType

    def set_WhenSeen(self, aWhenSeen):
        self.aircraftWhenSeen = aWhenSeen

    def get_WhenSeen(self):        return self.aircraftWhenSeen

    def set_WhenSeenComputer(self, aWhenSeenComputer):
        self.aircraftWhenSeenComputer = aWhenSeenComputer

    def get_WhenSeenComputer(self):
        return self.aircraftWhenSeenComputer

    def set_Interesting(self, aIntereesting):
        self.aircraftInteresting = aIntereesting

    def get_Interesting(self):
        return self.aircraftInteresting

    def set_AlertTime(self, aTime):
        self.aircraftAlertTime = aTime

    def get_AlertTime(self):
        return self.aircraftAlertTime  
## end Aircraft class