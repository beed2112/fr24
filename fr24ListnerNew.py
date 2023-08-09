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
    for p in noHitSession:
        age = lastCleanupTimeAircraft - p.noHitWhenSeenComputer
        ageMinutes = age.total_seconds() / 60
        if (ageMinutes >  purgeMinutesAircraft):
           # if (p.aircraftID in aircraftSession):
               noHitSession.pop(count)
        count += 1    
    return 

 
# cleanup aged aircraft 
def cleanAircraft():
   # global aircraftSession
    count = 0
    for p in aircraftSession:
        age = lastCleanupTimeAircraft - p.aircraftWhenSeenComputer
        ageMinutes = age.total_seconds() / 60
        if (ageMinutes >  purgeMinutesAircraft):
           # if (p.aircraftID in aircraftSession):
               aircraftSession.pop(count)
        count += 1    
    return 

#check Object to see if aircraft has been seen this session
def isKnownPlane(aircraftID):
    global aircraftSession
    for p in aircraftSession:
        if( p.aircraftID == aircraftID):
            icaohex =aircraftID 
            owners = p.aircraftOwner
            operatorFlagCode = p.aircraftOperatorFlagCode
            strReg = p.aircraftRegistration
            strType =p.aircraftType 
            epochTime =  p.aircraftWhenSeenComputer
            interesting = p.aircraftInteresting
            knownPlane = "True"
            print("known plane - local DB")
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
        if( p.noHitID == aircraftID):
            print("known no hit")
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
        cur.execute("INSERT INTO AIRCRAFT VALUES(?,?,?,?,?,?,?);",(icaohex, owners, strICAO, strReg, strType, epochTime, interesting ))
       # cur.execute("INSERT INTO AIRCRAFT VALUES('icaohex2','2','3','4','5', 6);")
        print("unknown plane - adding  aircraft row") 
        cur = conn.commit
        cur = conn.close   

#add an aircraft to the session object
def outPutAircraft():
    global mqttOutColor
    adsbExchangeBaseFull = adsbExchangeBase + str(icaohex) 
    itemNum = returnPlaneIndex(str(icaohex))
    outcolor= setOutcolor
    mqttOutColor = "TFT_WHITE"
    minutes = 0 

    #check strICAO first character - set color - will get overridden if "interesting" 
        
    if (str(aircraftSession[itemNum].get_Interesting())[0:1] == 'a'):
        mqttOutColor = "TFT_BLUE"
           
    outcolor="green"
    mqttOutColor = "TFT_GREEN"  
    timeSince = datetime.datetime.now() - aircraftSession[itemNum].get_AlertTime() 
    minutes = timeSince.total_seconds() / 60

    if ((aircraftSession[itemNum].get_AlertTime()) == aircraftSession[itemNum].get_WhenSeenComputer() or minutes > 15):
        outcolor="yellow" 
        mqttOutColor = "TFT_YELLOW"  
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
        #alertCount  += 1
        cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/alerts -u me -P me -m "' + str(alertCount) + '"'
        os.system(cmd) 
        conn = create_connection(database)
        cur = conn.cursor()
        epochTime = time.time() 
        cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);",(icaohex,epochTime ))
        cur = conn.commit
        cur = conn.close             
    #outLine = time.asctime(time.localtime(time.time()))+ " | " + str(aircraftSession[itemNum].get_WhenSeen()) + " | " + str(aircraftSession[itemNum].get_aircraftID())+ " | "+ str(aircraftSession[itemNum].get_Registration())  + " | " + str(aircraftSession[itemNum].get_Owner())+ " | " + str(aircraftSession[itemNum].get_OperatorFlagCode()) + " | " + str(aircraftSession[itemNum].get_Type() + " | " +  dataSource + " | " + adsbExchangeBaseFull) 
    
    #outLine = dataSource + " | " +  str(aircraftSession[itemNum].get_aircraftID())+ " | "+ str(aircraftSession[itemNum].get_Registration())  + " | " + str(aircraftSession[itemNum].get_Owner())+ " | " + str(aircraftSession[itemNum].get_OperatorFlagCode()) + " | " + str(aircraftSession[itemNum].get_Type() + " | " +  adsbExchangeBaseFull) 
    outLine = str(aircraftSession[itemNum].get_aircraftID())+ " | "+ str(aircraftSession[itemNum].get_Registration())  + " | " + str(aircraftSession[itemNum].get_Owner())+ " | " + str(aircraftSession[itemNum].get_OperatorFlagCode()) + " | " + str(aircraftSession[itemNum].get_Type() + " | " +  adsbExchangeBaseFull) 
    mqttOutLine = str( mqttOutColor) + "|" + str(aircraftSession[itemNum].get_aircraftID()) + " "+ str(aircraftSession[itemNum].get_Registration())  + " " + str(aircraftSession[itemNum].get_Owner())+ " " + str(aircraftSession[itemNum].get_OperatorFlagCode()) + " " + str(aircraftSession[itemNum].get_Type()) 
  
    print(colored(outLine, outcolor))    

    cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/console -u me -P me -m "'  + mqttOutLine +'"'
    os.system(cmd) 
                            
def addAircraft(aircraftID):

    global aircraftSession
    #global icaoData
    global localtime
    global interestingAircraftCount 
    global strICAO 
    global strReg 
    global strType
    global strAircraftID 
    global owners
    global interesting
    global filteredAircraft



   

    p = Aircraft(aircraftID)
    p.set_Registration(strReg)
    p.set_OperatorFlagCode(strICAO)
    p.set_Type(strType)
    p.set_Owner(owners)
    localtime = time.asctime( time.localtime(time.time()) )
    localtimeComputer = datetime.datetime.now()
    p.set_WhenSeen(str(localtime))
    p.set_WhenSeenComputer(localtimeComputer)


# going to add a column to table  AIRCRAFTINTERSTING -- moving to one aircraft DB 
    if (interestingAircraft()):
        p.set_Interesting("True")
        p.set_AlertTime(localtimeComputer)
        #add the aircraft to the database
        #add a seen record
        interesting = "True"
    else:
        p.set_Interesting("False")
        interesting = "False" 
            
    if strICAO not in excludeOperatorList:        
            addAircraftDB(aircraftID)  
            conn = create_connection(database)
            cur = conn.cursor()
            epochTime = time.time() 
            cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);",(icaohex,epochTime ))
            cur = conn.commit
            cur = conn.close 
            aircraftSession.append(p)
            outPutAircraft()
    else:
         filteredAircraft = filteredAircraft +1  
#    return

#is this an aircraft we are interested in 

def interestingAircraft():
    #owners=icao_data['RegisteredOwners']
    #strICAO = str(icao_data['OperatorFlagCod
    #strReg = str(icao_data['Registration'])
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
"""  
CREATE TABLE AIRCRAFT(                                                                                                                                                                                                                       
    AIRCRAFTID TEXT PRIMARY KEY NOT NULL,                                                                                                                                                                                                    
    AIRCRAFTOWNER TEXT KEY NOT NULL,
    AIRCRAFTOPERATORFLAGCODE TEXT NOT NULL,
    AIRCRAFTREGISTRATION TEXT NOT NULL,
    AIRCRAFTTYPE TEXT NOT NULL,
    AIRCRAFTFIRSTSEENEPOCH INT NOT NULL
, AIRCRAFTINTERESTING);

"""

def isKnownPlaneDB(aircraftID):
    global knownPlane
    global strICAO
    global owners
    global strReg
# create a database connection
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT * FROM AIRCRAFT WHERE AIRCRAFTID=?;", (aircraftID,))

    rows = cur.fetchall()
    cur.close 

    for row in rows:
        #print("info avail locally")

        icaohex =row[0]
        owners =row[1]
        operatorFlagCode =row[2]
        strReg =row[3]
        strType =row[4]
        epochTime =row[5]
        interesting =row[6]
        knownPlane = "True"
        
        strICAO = str(operatorFlagCode)
        strAircraftID = str(aircraftID)
        p = Aircraft(str(aircraftID))
        p.set_Registration( strReg)
        p.set_OperatorFlagCode(strICAO)
        p.set_Type(strType)
        p.set_Owner(owners)
        localtime = time.asctime( time.localtime(time.time()) )
        localtimeComputer = datetime.datetime.now()
        p.set_WhenSeen(str(localtime))
        p.set_WhenSeenComputer(localtimeComputer)
        p.set_Interesting(interesting)


        if (interestingAircraft()):
            p.set_Interesting("True")
            p.set_AlertTime(localtimeComputer)
            #add the aircraft to the database
            #add a seen record
            interesting = "True"
        else:
            p.set_Interesting("False")
            interesting = "False" 

        if interesting == "True":
            p.set_AlertTime(localtimeComputer)
            #add the aircraft to the database
            #add a seen record
            conn = create_connection(database)
            cur = conn.cursor()
            epochTime = time.time() 
            cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);",(icaohex,epochTime ))
            cur = conn.commit
            cur = conn.close
            print("known adding sighting info")
        else:
            p.set_Interesting("False")
            interesting = "False" 

        aircraftSession.append(p)
        #outPutAircraft()
        return True
    return False    
    
###
def checkFAA(aircraftID):
    global knownPlane
# create a database connection
    conn = create_connection(database)
    cur = conn.cursor()
    aircraftIDq = aircraftID + "%"
    cur.execute("SELECT * FROM MASTER WHERE AIRCRAFTID =?;", (aircraftID,))

    rows = cur.fetchall()
    cur.close 

    for row in rows:
        print("info avail locally")

        icaohex =row[2]
        owners =row[1]
        operatorFlagCode ="xxx"
        strReg ="N" + row[0]
        strType ="xxx"
        epochTime = datetime.datetime.now()
        interesting = "False"
        knownPlane = "True"
        
        owners = owners.rstrip()
        strICAO = str(operatorFlagCode)
        strAircraftID = str(aircraftID)
        p = Aircraft(str(aircraftID))
        p.set_Registration( strReg)
        p.set_OperatorFlagCode(strICAO)
        p.set_Type(strType)
        p.set_Owner(owners)
        localtime = time.asctime( time.localtime(time.time()) )
        localtimeComputer = datetime.datetime.now()
        p.set_WhenSeen(str(localtime))
        p.set_WhenSeenComputer(localtimeComputer)
        p.set_Interesting(interesting)

        if interesting == "True":
            p.set_AlertTime(localtimeComputer)
            #add the aircraft to the database
            #add a seen record
            conn = create_connection(database)
            cur = conn.cursor()
            epochTime = time.time() 
            cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);",(icaohex,epochTime ))
            cur = conn.commit
            cur = conn.close
        else:
            p.set_Interesting("False")
            interesting = "False" 

        aircraftSession.append(p)
        outPutAircraft()
        return True
    return False 
###  

def dbKnownNoHit(aircraftID):
    

# create a database connection
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT * FROM NOHITAIRCRAFT WHERE AIRCRAFTID=?;", (aircraftID,))

    rows = cur.fetchall()
    cur.close 

    for row in rows:
        #print(row)
       # knownNoHitDB += 1
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

#not called
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
    cur.execute("INSERT INTO AIRCRAFTNOTINTERESTING VALUES(?,?,?,?,?,?);",(icaohex, owners, strICAO, strReg, strType, epochTime, interesting ))
    #cur.execute("INSERT INTO AIRCRAFT VALUES('icaohex2','2','3','4','5', 6);")
    cur = conn.commit
    cur = conn.close      
    return True        


##-----------------------------------------------------------------------------------------------------------------------------###
### mainline

sampling_period =60

sampling_period_seconds = int(sampling_period)

excludeOperatorList="LXJ,AAL,ASA,UAL,SWA,FFT,SKW,WJA,FLE,ASH,DAL,ENY,NKS,VOI,JBU,WSW,UPS,SWQ,ABX,FDX,QXE,SLI,EJA,JZA,ROU,GAJ,FDY,CFS,NJAS"
watchlistOwner= ["ACES","Missile Defense Agency","NASCAR", "Motorsports","Federal", "United States", "Oprah", "Police", "State Farm", "Sherrif", "Arizona Department", "NASA", "Air Force", "Museum", "Google", "Apple", "Penske" , "Cardinals" , "Stewart-Haas" , "Tanker"]
watchReg="N44SF,N812LE,N353P,N781MM,N88WR,N383LS,N78HV,N4DP,N9165H,N519JG,N280NV"
watchICAO="F16,S211,BE18,AJET,KMAX,HGT,ST75,RRR,MRF1,L1P,T6,BGR,TNK"

global aircraftSession
global noHitSession
global icao_data
global icao_response
global icaohex
global database
global knownPlane
global strICAO 
global localResolve
global webserviceCalls
global lastCleanupTimeAircraft
global purgeMinutesAircraft
global knownAircraft
global filteredAircraft 
global knownNoHitDB
global setOutcolor
global mqttOutColor

database = "/fr24db/aircraftMon.db" 

aircraftSession = []
noHitSession = []

filteredAircraft  = 0 
interestingAircraftCount = 0
alertCount = 0 
nohit=0
webServiceError=0

webserviceCalls = 0 

totalAircraftCount = 0

localResolve = 0 
localMemResolve = 0 
knownNoHitDB = 0

startTime = time.asctime(time.localtime(time.time()))

lastCleanupTimeAircraft = datetime.datetime.now()
purgeMinutesAircraft = 240


# grab aircraft.json from the reciever

receiver_url ='http://192.168.0.116'
adsbExchangeBase = 'https://globe.adsbexchange.com/?icao='
while True:
  
  aircraftCount= 0 
     


  try:
      
      r = requests.get(f'{receiver_url}/dump1090/data/aircraft.json', timeout=(5,5))
      if r.status_code != 200:
        raise ValueError(f'ERROR: getting aircraft json data :{r.text}')
        
      aircraft_data = r.json()
      now = aircraft_data['now']
      info_data = {
      'now': now,
      'aircraft_count' : len(aircraft_data['aircraft']),
      'messages': aircraft_data['messages']
       }
      
      aircraftCount= info_data['aircraft_count']
  except:
      aircraftCount= 0 

  totalAircraftCount = totalAircraftCount + aircraftCount

  part1a =  "+++--Curr " + time.asctime(time.localtime(time.time()))
  part1 =  "+++" 
  part2 =  "-- Strt " + startTime + "--tot seen " + str(totalAircraftCount) + "-- cur " + str(aircraftCount)
  part4 = "--wsCall " + str(webserviceCalls) + "--wsErr " + str(webServiceError)
  part5 = "--knwnNoHit " + str(knownNoHitDB) +  "--nohit " + str(nohit) + "--lclDB " + str(localResolve)
  part6 = "lclMem " + str(localMemResolve) + "--+++"
  #outline = part1 + part2 + "--" + part3 + "--" + "--"+ part4 + part5 +  "--"  + part6
  outline =  part1 + part2 +  "--" + part4 + "--" + part5 +  "--"  + part6
  print (outline) 

  mqttOutColor =  "TFT_ORANGE" 
  mqttOutLine = str(mqttOutColor) + "|" +  part1a + part2 
  cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/console -u me -P me -m "'  + mqttOutLine +'"'
  os.system(cmd) 


#loop thru the aircraft 
  i = 00

  while i < aircraftCount:
   icaohex = aircraft_data['aircraft'][i]['hex']
 
   i += 1
   setOutcolor = "white"
   mqttOutcolor = "TFT_WHITE"  
   strICAO = ""
   knownNoHitAircraft = "False"
   knownAircraft = "False"
   if isKnownPlane(icaohex):
      knownAircraft = "True"
      localMemResolve += 1
      dataSource = "memory    "
      outPutAircraft()
   else: 

    if isKnownPlaneDB(icaohex):
        knownAircraft = "True"
        localResolve += 1
        dataSource = "local     "
        outPutAircraft()
        #addAircraft(icaohex)
    else:
        #if ( not isKnownNoHitCheck(icaohex) ):
        #if ( dbKnownNoHit(icaohex) == "False" ):
        if  not dbKnownNoHit(icaohex) :
                try:
                    knownNoHitAircraft = "False" 
                    webserviceCalls += 1
                    icao_response = requests.get(f'https://hexdb.io/api/v1/aircraft/{icaohex}', timeout=(15,15))
                    icao_data = icao_response.json()
                    if (icao_response.status_code == 200 ):
                        strICAO = str(icao_data['OperatorFlagCode'])
                        owners=icao_data['RegisteredOwners']
                        strReg = str(icao_data['Registration'])
                        strType =str(icao_data['Type'])
                        strAircraftID = str(icaohex)
                        knownAircraft = "True"
                        dataSource = "web       "
                        setOutcolor = "cyan"
                        mqttOutColor = "TFT_CYAN"  
                        #print ("++++++++++++++++++++++++++++++++++++++++NEW PLANE")
                        addAircraft(icaohex)
                        
                    else:
                            addNoHit(icaohex)
                            nohit += 1
                            checkFAA(icaohex)
                            cmd = 'mosquitto_pub -h 192.168.0.253  -t planes/nohit -u me -P me -m "' + icaohex + " " + str(nohit) +'"'
                            os.system(cmd) 
                            addIfNewNoHit(icaohex)    
                            #print ("++++++++++++++++++++++++++++++++++++++++NEW NOHIT")  
                except (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, Exception) as e: 
                    strICAO = "ERROR"
                    webServiceError += 1
                    print(e)
        else:
            knownNoHitDB += 1

   timeSinceLastCleanupAircraft = datetime.datetime.now() - lastCleanupTimeAircraft
   minutesSinceLastCleanupAircraft = timeSinceLastCleanupAircraft.total_seconds() / 60

   if (minutesSinceLastCleanupAircraft> purgeMinutesAircraft):
       #cleanAircraft()
       lastCleanupTimeAircraft = datetime.datetime.now()
       hold1 = len(aircraftSession)
       cleanAircraft()
       hold2 = len(aircraftSession)
       outLine = time.asctime(time.localtime(time.time()))+ " | Aircraft memory clean up time before " + str(hold1) + " | after " + str(hold2) 
       outcolor = "blue"
       print(colored(outLine, outcolor)) 
       #aircraftSession = []
       hold1 = len(noHitSession)
       cleanNoHitAircraft()
       hold2 = len(noHitSession)
       outLine = time.asctime(time.localtime(time.time()))+ " | noHit memory clean up time before " + str(hold1) + " | after " + str(hold2) 
       outcolor = "yellow"
       print(colored(outLine, outcolor)) 
       
  myCounbt = 0   
  for  mycount in range(sampling_period_seconds):
   print(".",end="")
   time.sleep(1) 
  print("")
   
  # print (str(aircraftCount) + " - " + str(i) + " - " + icaohex  + " - " + strICAO + " -known nohit " + knownNoHitAircraft + " -known  " + knownAircraft )

   








# no code below here 

# dealing with time   https://thispointer.com/how-to-add-minutes-to-datetime-in-python/

# https://globe.adsbexchange.com/?icao=aa8ef0
# aa43ee | N7600P | SAS Institute Inc | F9EX | Falcon 900EX EASy    z
