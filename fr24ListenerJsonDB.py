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
#sys.path.append('/home/beed2112/fr24')
from aircraft import Aircraft
from nohitAircraft import noHit

# cleanup aged Noaircraft 
def cleanNoHitAircraft():
   # global aircraftSession
    count = 0
    removed = 0
    kept = 0 
    for p in noHitSession:
        age = lastCleanupTimeAircraft - p.noHitWhenSeenComputer
        ageMinutes = age.total_seconds() / 60
        if (ageMinutes >  (purgeMinutesNoHit)):
           # if (p.aircraftID in aircraftSession):
               noHitSession.pop(count)
               removed +=1
        else:  
           kept += 1
        count += 1    
    outLine = " ----------> " + time.asctime(time.localtime(time.time()))+ " Removed NoHit Aircraft " +  str(removed)
    outcolor = "blue"
    print(colored(outLine, outcolor))
    outLine = " ----------> " + time.asctime(time.localtime(time.time()))+ "      Kept NoHit Aircraft " +  str(kept)  
    print(colored(outLine, outcolor))  
    return 

 
# cleanup aged aircraft 
def cleanAircraft():
   # global aircraftSession
    count = 0
    removed = 0 
    kept = 0 
    for p in aircraftSession:    
        age = lastCleanupTimeNoHit - p.aircraftWhenSeenComputer
        ageMinutes = age.total_seconds() / 60
        if (ageMinutes >  purgeMinutesAircraft):
           # if (p.aircraftID in aircraftSession):
               aircraftSession.pop(count)
               removed +=1
        else:
           kept +=1  
        count += 1  
    outLine = " ----------> " + time.asctime(time.localtime(time.time()))+ "      Removed Aircraft " +  str(removed)
    outcolor = "blue"
    print(colored(outLine, outcolor))     
    outLine = " ----------> " + time.asctime(time.localtime(time.time()))+ "     Kept Aircraft " +  str(kept)  
    print(colored(outLine, outcolor))  
    return 

#check Object to see if aircraft has been seen this session
def isKnownPlane(aircraftID):
    global aircraftSession
    for p in aircraftSession:
        if( p.aircraftID == aircraftID):
            return True
    return False

# return the index of the aircraft 
def returnPlaneIndex(aircraftID):
    global aircraftSession
    count = 0
    for p in aircraftSession:
        if( p.aircraftID == aircraftID): 
            return count
        count = count + 1
    return -1 

# see if we have already failed to find info on the aircraft 
def isKnownNoHitCheck(aircraftID):
    
    for p in noHitSession:
        if( p == aircraftID):
            return True
    return False

# add an aircraft to the list used during the session
def addNoHit(aircraftID):
    p = noHit(str(aircraftID))
    localtime = time.asctime( time.localtime(time.time()) )
    localtimeComputer = datetime.datetime.now()
    p.set_noHitWhenSeen(str(localtime))
    p.set_noHitWhenSeenComputer(localtimeComputer)
    noHitSession.append(p)
# and records to DB when interesting aircraft identified
def addAircraftDB(icaohex):
    if (not isKnownPlaneDB(str(icaohex))):
        conn = create_connection(database)
        cur = conn.cursor()
        epochTime = time.time() 
        cur.execute("INSERT INTO AIRCRAFT VALUES(?,?,?,?,?,?);",(icaohex, owners, strICAO, strReg, strType, epochTime ))
        #cur.execute("INSERT INTO AIRCRAFT VALUES('icaohex2','2','3','4','5', 6);")
        cur = conn.commit
        cur = conn.close   

#add an aircraft to the session object

def addAircraft(aircraftID):

    global aircraftSession
    global icaoData
    global localtime
    global interestingAircraftCount 
    global strICAO 
    global strReg 
    global strType
    global strAircraftID 
    global owners
#    icao_response = requests.get(f'https://hexdb.io/api/v1/aircraft/{aircraftID}')

#    icao_data = icao_response.json()
    icaoData ="False"
 #   if icao_response.status_code == 200:
    icaoData ="True"
    if str(icao_data['OperatorFlagCode']) not in excludeOperatorList:
        owners=icao_data['RegisteredOwners']
        strICAO = str(icao_data['OperatorFlagCode'])
        strReg = str(icao_data['Registration'])
        strType =str(icao_data['Type'])
        strAircraftID = str(aircraftID)
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
            #add the aircraft to the database
            #add a seen record
            addAircraftDB(aircraftID)  
            conn = create_connection(database)
            cur = conn.cursor()
            epochTime = time.time() 
            cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);",(icaohex,epochTime ))
            cur = conn.commit
            cur = conn.close 
        else:
            p.set_Interesting("False")
            addIfNewNotInterestinig(aircraftID)

        aircraftSession.append(p)
 
#    return

#is this an aircraft we are interested in 

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
        conn = sqlite3.connect(db_file , isolation_level = None)
    except Error as e:
        print(e)

    return conn

def isKnownPlaneDB(aircraftID):
    
# create a database connection
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT * FROM AIRCRAFT WHERE AIRCRAFTID=?;", (aircraftID,))

    rows = cur.fetchall()
    cur.close 

    for row in rows:
        #print(row)
        return True
    return False    
    
    

def addIfNewNoHit(aircraftID):
    

# create a database connection
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT * FROM NOHITAIRCRAFT WHERE AIRCRAFTID=?;", (aircraftID,))

    rows = cur.fetchall()
    cur.close 

    for row in rows:
        #print(row)
        return False
    conn1 = create_connection(database)
    cur1 = conn1.cursor()
    epochTime = time.time() 
    cur1.execute("INSERT INTO NOHITAIRCRAFT VALUES(?,?);",(aircraftID,epochTime ))
    cur1 = conn1.commit
    cur1 = conn1.close     
    return True        


def addIfNewNotInterestinig(aircraftID):
    

# create a database connection
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT * FROM AIRCRAFTNOTINTERESTING WHERE AIRCRAFTID=?;", (aircraftID,))

    rows = cur.fetchall()
    cur.close 

    for row in rows:
        #print(row)
        return False
    conn = create_connection(database)
    cur = conn.cursor()
    epochTime = time.time() 
    cur.execute("INSERT INTO AIRCRAFTNOTINTERESTING VALUES(?,?,?,?,?,?);",(icaohex, owners, strICAO, strReg, strType, epochTime ))
    #cur.execute("INSERT INTO AIRCRAFT VALUES('icaohex2','2','3','4','5', 6);")
    cur = conn.commit
    cur = conn.close      
    return True        


##-----------------------------------------------------------------------------------------------------------------------------###
### mainline

sampling_period =60

sampling_period_seconds = int(sampling_period)

#Sat Feb 25 10:47:07 2023 | Sat Feb 25 10:47:07 2023 | acb004 | N9165H | Private | FA62 | M-62A-3 PT-26 | https://globe.adsbexchange.com/?icao=acb004

excludeOperatorList="LXJ,AAL,ASA,UAL,SWA,FFT,SKW,WJA,FLE,ASH,DAL,ENY,NKS,VOI,JBU,WSW"
watchlistOwner= ["Missile Defense Agency","NASCAR", "Motorsports","Federal", "United States", "Oprah", "Police", "State Farm", "Sherrif", "Arizona Department", "NASA", "Air Force", "Museum", "Google", "Apple", "Penske" , "Cardinals" , "Stewart-Haas"]
watchReg="N44SF,N812LE,N353P,N781MM,N88WR,N383LS,N78HV,N4DP,N9165H,N519JG"
watchICAO="F16,S211,BE18,AJET,KMAX,HGT,ST75,RRR,MRF1,CKS,L1P,T6,BGR"

global aircraftSession
global noHitSession
global icao_data
global icao_response
global icaohex
global database
global purgeMinutesAircraft
global lastCleanupTimeAircraft
global purgeMinutesNoHit
global lastCleanupTimeNoHit
database = "/home/beed2112/fr24/aircraftMon.db" 

aircraftSession = []
noHitSession = []

interestingAircraftCount = 0
alertCount = 0 
nohit=0
lastCleanupTimeAircraft = datetime.datetime.now()
purgeMinutesAircraft = 180

lastCleanupTimeNoHit = datetime.datetime.now()
purgeMinutesNoHit = 8

#wwII trainer no hit example https://globe.adsbexchange.com/?icao=a2d458

# grab aircraft.json from the reciever

receiver_url ='http://192.168.0.116'
adsbExchangeBase = 'https://globe.adsbexchange.com/?icao='
go = 0 
while go == 0 :
  #print ("talk to the pi")
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
  
  
  part1 = "+++--------------------------------------------------------------------------------------------------------------------------------------------"
  part2 = time.asctime(time.localtime(time.time()))
  part3 = str(info_data['aircraft_count'])
  part4 = str(len(aircraftSession))
  part5 = str(len(noHitSession))
  part6 = "----+++"

  outline = part1 + part2 + "--" + part3 + "--" + part4 + "--" + part5 + "--" + part6
  print (outline)

#loop thru the aircraft 
  i = 00

  while i < info_data['aircraft_count']:
   icaohex = aircraft_data['aircraft'][i]['hex']
   knownNoHit = "False"

   if ( not isKnownNoHitCheck(icaohex) ):
      knownNoHit = "False" 
      #print ("talk to the webservice")
      icao_response = requests.get(f'https://hexdb.io/api/v1/aircraft/{icaohex}')
      icao_data = icao_response.json()

      if (icao_response.status_code == 200 ):
          #if str(icao_data['OperatorFlagCode']) not in excludeOperatorList or not ( isKnownPlane(str(icaohex))):  
          if str(icao_data['OperatorFlagCode']) not in excludeOperatorList:
              knownPlane= "False"
              if(len(aircraftSession) > 0):
                  #Check if Plane ID Exists
                  if( isKnownPlane(str(icaohex))):
                  #if str(icao_data['OperatorFlagCode']) not in excludeOperatorList:
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
                    #mqout = str(aircraftSession[itemNum].get_Registration())  + " " + str(aircraftSession[itemNum].get_Owner()) +"  " + str(aircraftSession[itemNum].get_Type()) 
                    mqout =  str(aircraftSession[itemNum].get_Owner()) +". " + str(aircraftSession[itemNum].get_Type()) 
                    localtime = time.asctime( time.localtime(time.time()) )
                    mqout2 = localtime  + " " + str(aircraftSession[itemNum].get_Registration())  + " " + str(aircraftSession[itemNum].get_Owner()) +"  " + str(aircraftSession[itemNum].get_Type() +"  " + adsbExchangeBaseFull) 
                    cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/watchfor -u me -P me -m "' + mqout + '"'
                    os.system(cmd)
                    cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/watchforLong -u me -P me -m "' + mqout2 + '"'
                    os.system(cmd) 
                    alertCount  += 1
                    cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/alerts -u me -P me -m "' + str(alertCount) + '"'
                    os.system(cmd) 
                    conn = create_connection(database)
                    cur = conn.cursor()
                    epochTime = time.time() 
                    cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);",(icaohex,epochTime ))
                    cur = conn.commit
                    cur = conn.close             
              
              outLine = time.asctime(time.localtime(time.time()))+ " | " + str(aircraftSession[itemNum].get_WhenSeen()) + " | " + str(aircraftSession[itemNum].get_aircraftID())+ " | "+ str(aircraftSession[itemNum].get_Registration())  + " | " + str(aircraftSession[itemNum].get_Owner())+ " | " + str(aircraftSession[itemNum].get_OperatorFlagCode()) + " | " + str(aircraftSession[itemNum].get_Type() + " | " + adsbExchangeBaseFull) 
              print(colored(outLine, outcolor))    
              
      else:
        #noHitSession.append(icaohex)
        addNoHit(icaohex)
        nohit += 1 
        cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/nohit -u me -P me -m "' + icaohex + " " + str(nohit) +'"'
        os.system(cmd) 
        addIfNewNoHit(icaohex)


   
   timeSinceLastCleanupAircraft = datetime.datetime.now() - lastCleanupTimeAircraft
   minutesSinceLastCleanupAircraft = timeSinceLastCleanupAircraft.total_seconds() / 60

   if (minutesSinceLastCleanupAircraft> purgeMinutesAircraft):
       #cleanAircraft()
       lastCleanupTimeAircraft = datetime.datetime.now()
       aircraftSession = []
       
   timeSinceLastCleanupNohit = datetime.datetime.now() - lastCleanupTimeNoHit
   minutesSinceLastCleanupNohit = timeSinceLastCleanupNohit.total_seconds() / 60
 
   if (minutesSinceLastCleanupNohit > purgeMinutesNoHit):

       #cleanNoHitAircraft()
       noHitSession = []
       lastCleanupTimeNoHit = datetime.datetime.now()
 
 
 
   i += 1
   myobj =  datetime.datetime.now()
   myHour =  myobj.hour
   myMinute = myobj.minute

   if (myHour == 4):
       if (myMinute == 20):
          print("exitting program")
          go =5
          x = requests.get(f'https://foobar.foo')
           


# dealing with time   https://thispointer.com/how-to-add-minutes-to-datetime-in-python/

# https://globe.adsbexchange.com/?icao=aa8ef0
# aa43ee | N7600P | SAS Institute Inc | F9EX | Falcon 900EX EASy    z
