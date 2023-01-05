import sys
import os
import json
import time
#from datetime import date
import datetime
import requests
from termcolor import colored
import sqlite3
from sqlite3 import Error



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

    def get_WhenSeen(self):
        return self.aircraftWhenSeen

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

def isKnownNoHitCheck(aircraftID):
    
    for p in noHitSession:
        if( p == aircraftID):
            return True
    return False


def addNoHit(aircraftID):
    p = noHit(str(aircraftID))
    localtime = time.asctime( time.localtime(time.time()) )
    localtimeComputer = datetime.datetime.now()
    p.set_noHitWhenSeen(str(localtime))
    p.set_noHitWhenSeenComputer(localtimeComputer)
    noHitSession.append(p)

def addAircraft(aircraftID):

    global aircraftSession
    global icaoData
    global localtime
    global interestingAircraftCount 

#    icao_response = requests.get(f'https://hexdb.io/api/v1/aircraft/{aircraftID}')

#    icao_data = icao_response.json()
    icaoData ="False"
 #   if icao_response.status_code == 200:
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
        localtimeComputer = datetime.datetime.now()
        p.set_WhenSeen(str(localtime))
        p.set_WhenSeenComputer(localtimeComputer)

        if (interestingAircraft()):
            p.set_Interesting("True")
            p.set_AlertTime(localtimeComputer)

        else:
            p.set_Interesting("False")

        aircraftSession.append(p)
            
#    return

def interestingAircraft():
    owners=icao_data['RegisteredOwners']
    strICAO = str(icao_data['OperatorFlagCode'])
    strReg = str(icao_data['Registration'])
    global interestingAircraftCount 
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
       interestingAircraftCount  += 1
       cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/interestingAircraft -u me -P me -m "' + str(interestingAircraftCount) + '"'
       os.system(cmd) 
       return True
       
    else:
        return False

##-----------------------------------------------------------------------------------------------------------------------------###
## this is DB interaction code





def create_connection(db_file):
  
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def isKnownPlaneDB(conn, aircraftID):

    cur = conn.cursor()
    cur.execute("SELECT * FROM AIRCRAFT WHERE AIRCRAFTID=?", (aircraftID,))

    rows = cur.fetchall()

    for row in rows:
        print(row)
        return True
    return False    












##-----------------------------------------------------------------------------------------------------------------------------###
### mainline

sampling_period =60

sampling_period_seconds = int(sampling_period)

excludeOperatorList="AAL,ASA,UAL,SWA,FFT,SKW,WJA,FLE,AAY,ASH,DAL,ENY,NKS,VOI,JBU,WSW"
watchlistOwner= ["United States", "Orah", "Police", "State Farm", "Sherrif", "Arizona Department", "NASA", "Air Force", "Museum", "Google", "Apple", "Penske"]
watchReg="N44SF,N812LE,N353P"
watchICAO="F16,S211,BE18,AJET,KMAX,HGT,ST75,RRR,MRF1"

global aircraftSession
global noHitSession
global icao_data
global icao_response

aircraftSession = []
noHitSession = []

interestingAircraftCount = 0
alertCount = 0 
nohit=0

database = "aircraftMon.db"

# create a database connection
conn = create_connection(database)



# grab aircraft.json from the reciever

receiver_url ='http://192.168.0.116'
adsbExchangeBase = 'https://globe.adsbexchange.com/?icao='
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
  
  
  
  print ("+++-------------------------------------------------------------------------------------------------------------------------------------------------------------+++")

#loop thru the aircraft 
  i = 00

  while i < info_data['aircraft_count']:
   icaohex = aircraft_data['aircraft'][i]['hex']
   knownNoHit = "False"

   if ( not isKnownNoHitCheck(icaohex) ):
      knownNoHit = "False" 
      icao_response = requests.get(f'https://hexdb.io/api/v1/aircraft/{icaohex}')
      icao_data = icao_response.json()

      if (icao_response.status_code == 200 ):
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
                      isKnownPlaneDB(conn, str(icaohex))
                
              else:
                  #Add Plane
                  addAircraft(str(icaohex))
                  itemNum = len(aircraftSession)-1
            
        
        
              cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/Aircraft -u me -P me -m "' + str(len(aircraftSession)) + '"'
              os.system(cmd)  
              
              adsbExchangeBaseFull = adsbExchangeBase + str(icaohex) 

              outcolor="white"
              minutes = 0 
              if (str(aircraftSession[itemNum].get_Interesting()) == 'True'):
                  outcolor="green"
                  timeSince = datetime.datetime.now() - aircraftSession[itemNum].get_AlertTime() 
                  minutes = timeSince.total_seconds() / 60
                  if ((aircraftSession[itemNum].get_AlertTime()) == aircraftSession[itemNum].get_WhenSeenComputer() or minutes > 15):
                    outcolor="yellow" 
                    localtimeComputer = datetime.datetime.now()
                    aircraftSession[itemNum].set_AlertTime(localtimeComputer)
                    mqout = str(aircraftSession[itemNum].get_Registration())  + " " + str(aircraftSession[itemNum].get_Owner()) +"  " + str(aircraftSession[itemNum].get_Type() +"  " + adsbExchangeBaseFull) 
                    localtime = time.asctime( time.localtime(time.time()) )
                    mqout2 = localtime  + " " + str(aircraftSession[itemNum].get_Registration())  + " " + str(aircraftSession[itemNum].get_Owner()) +"  " + str(aircraftSession[itemNum].get_Type() +"  " + adsbExchangeBaseFull) 
                    cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/watchfor -u me -P me -m "' + mqout + '"'
                    os.system(cmd)
                    cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/watchforLong -u me -P me -m "' + mqout2 + '"'
                    os.system(cmd) 
                    alertCount  += 1
                    cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/alerts -u me -P me -m "' + str(alertCount) + '"'
                    os.system(cmd)         

              
              outLine = time.asctime(time.localtime(time.time()))+ " | " + str(aircraftSession[itemNum].get_WhenSeen()) + " | " + str(aircraftSession[itemNum].get_aircraftID())+ " | "+ str(aircraftSession[itemNum].get_Registration())  + " | " + str(aircraftSession[itemNum].get_Owner())+ " | " + str(aircraftSession[itemNum].get_OperatorFlagCode()) + " | " + str(aircraftSession[itemNum].get_Type() + " | " + adsbExchangeBaseFull) 
             #print(str(aircraftSession[len(aircraftSession)-1].get_WhenSeen()) )
             #outLine=str(localtime) +" | " + str(icaohex)+ " | "+ str(icao_data['Registration'])+ " | "+ str(icao_data['ICAOTypeCode'])+ " | "+ str(icao_data['OperatorFlagCode'])+ " | "+ str(icao_data['RegisteredOwners'])+ " | "+ str(icao_data['Type'])
              print(colored(outLine, outcolor))    
      else:
        noHitSession.append(icaohex)
        nohit += 1 
        cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/nohit -u me -P me -m "' + icaohex + " " + str(nohit) +'"'
        os.system(cmd)  
   

   i += 1


# dealing with time   https://thispointer.com/how-to-add-minutes-to-datetime-in-python/

# https://globe.adsbexchange.com/?icao=aa8ef0
# aa43ee | N7600P | SAS Institute Inc | F9EX | Falcon 900EX EASy    z
