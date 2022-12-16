import sys
import os
import json
import time

import requests
from termcolor import colored





class Aircraft:
    "Aircraft Class"
    aircraftID = ""
    aircraftOwner = "" 
    aircraftOperatorFlagCode = ""
    aircraftRegistration = ""
    aircraftType = ""
    aircraftWhenSeen = ""

    def __init__(self, aircraftID):
        self.aircraftID = aircraftID
    
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

    def get_WhenSeen(self):
        return self.aircraftWhenSeen

    def set_Interesting(self, aIntereesting):
        self.aircraftInteresting = aIntereesting

    def get_Interesting(self):
        return self.aircraftInteresting

## end Aircraft class


def isKnownPlane(aircraftID):
    global aircraftSession
    for p in aircraftSession:
        if( p.aircraftID == aircraftID):
            return True
    return False

def returnPlaneIndex(aircraftID):
    global aircraftSession
    count = 0
    for p in aircraftSession:
        if( p.aircraftID == aircraftID):
            return count
        count = count + 1
    return -1 
        
def addAircraft(aircraftID):

    global aircraftSession
    global icaoData
    global localtime

    icao_response = requests.get(f'https://hexdb.io/api/v1/aircraft/{aircraftID}')

    icao_data = icao_response.json()
    icaoData ="False"
    if icao_response.status_code == 200:
        icaoData ="True"
        if str(icao_data['OperatorFlagCode']) not in excludeOperatorList:
            owners=icao_data['RegisteredOwners']
            strICAO = str(icao_data['OperatorFlagCode'])
            strReg = str(icao_data['Registration'])
            p = Aircraft(str(aircraftID))
            p.set_Registration(str(icao_data['Registration']))
            p.set_OperatorFlagCode(str(icao_data['OperatorFlagCode']))
            p.set_Type(str(icao_data['Type']))
            p.set_Owner(str(icao_data['RegisteredOwners']))
            localtime = time.asctime( time.localtime(time.time()) )
            p.set_WhenSeen(str(localtime))
            if (interestingAircraft()):
                p.set_Interesting("True")
            else:
                p.set_Interesting("False")

            aircraftSession.append(p)
            
    return

def interestingAircraft():
    owners=icao_data['RegisteredOwners']
    strICAO = str(icao_data['OperatorFlagCode'])
    strReg = str(icao_data['Registration'])

    interestCount = 0
    o= 0
    while o < len(watchlistOwner):
        if watchlistOwner[o] in owners:
            interestCount += 1
        o += 1

    if strICAO in watchICAO:
        interestCount += 1

    if strReg in watchReg:
        interestCount += 1        

    if interestCount > 0:
       return True
    else:
        return False


### mainline

sampling_period =60

sampling_period_seconds = int(sampling_period)

excludeOperatorList="AAL,ASA,UAL,SWA,FFT,SKW,WJA,FLE,AAY,ASH,DAL,ENY,NKS"
watchlistOwner= ["United States", "Utah Trustee", "Police", "Police", "State Farm", "Sherrif", "Arizona Department", "NASA", "Royal Canadian Air Force"]
watchReg="N44SF,N812LE"
watchICAO="F16,S211,BE18,AJET,KMAX,HGT,ST75"

global aircraftSession

aircraftSession = []



# grab aircraft.json from the reciever

receiver_url ='http://192.168.0.116'

while True:

  #r = requests.get(f'{receiver_url}/dump1090/{getIt}')
  r = requests.get(f'{receiver_url}/dump1090/data/aircraft.json')

  if r.status_code != 200:
    raise ValueError(f'ERROR: getting aircraft json data :{r.text}')

  aircraft_data = r.json()

  now = aircraft_data['now']
  info_data = {
    'now': now,
    'aircraft_count' : len(aircraft_data['aircraft']),
    'messages': aircraft_data['messages']
  }
  
  
  
  print ("+++------------------------------------------------------------------------------------------------------+++")

#loop thru the aircraft 
  i = 00
  while i < info_data['aircraft_count']:
   icaohex = aircraft_data['aircraft'][i]['hex']
   icao_response = requests.get(f'https://hexdb.io/api/v1/aircraft/{icaohex}')

   icao_data = icao_response.json()

   if icao_response.status_code == 200:
       if str(icao_data['OperatorFlagCode']) not in excludeOperatorList:

        knownPlane= "False"
        if(len(aircraftSession) > 0):
            #Check if Plane ID Exists
            if( isKnownPlane(str(icaohex))):
                #Get Plane Item # so we can update them
                itemNum = returnPlaneIndex(str(icaohex))
                #Update Plane seen time if current time + 15 min > current time seen value
                knownPlane= "True"
                
            else:
                #Add Plane
                addAircraft(str(icaohex))
                itemNum = len(aircraftSession)-1
               
        else:
            #Add Plane
            addAircraft(str(icaohex))
            itemNum = len(aircraftSession)-1
        
        outcolor="white"

        print(str(aircraftSession[itemNum].get_WhenSeen()) + " " + str(aircraftSession[itemNum].get_Owner()) + " " +  str(aircraftSession[itemNum].get_Interesting()) + " " + knownPlane) 
        #print(str(aircraftSession[len(aircraftSession)-1].get_WhenSeen()) )
        #outLine=str(localtime) +" | " + str(icaohex)+ " | "+ str(icao_data['Registration'])+ " | "+ str(icao_data['ICAOTypeCode'])+ " | "+ str(icao_data['OperatorFlagCode'])+ " | "+ str(icao_data['RegisteredOwners'])+ " | "+ str(icao_data['Type'])
        #print(colored(outLine, outcolor))    


   i += 1


# dealing with time   https://thispointer.com/how-to-add-minutes-to-datetime-in-python/



