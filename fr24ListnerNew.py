import sys
import os
import json
import time
import paho.mqtt.client as paho

#from datetime import date
import datetime
import requests
from termcolor import colored
import sqlite3
from sqlite3 import Error
from aircraft import Aircraft
from nohitAircraft import noHit
from datetime import datetime, timedelta  
global strICAO 

def outPutMQTT(outColor, outTopic, outMessage):

  mqttServer = "192.168.0.253"
  mqttUser = "me"
  mqttPass = "me"
  
  mqttOutLine = str(outColor) + "|" +  outMessage

  client = paho.Client()
  client.username_pw_set(mqttUser, mqttPass)
  
  client.connect(mqttServer)
  client.publish(outTopic, mqttOutLine)  

def outPutMQTTnoColor(outTopic, outMessage):

  mqttServer = "192.168.0.253"
  mqttUser = "me"
  mqttPass = "me"

  client = paho.Client()
  client.username_pw_set(mqttUser, mqttPass)
  myFooConnect = client.is_connected()
  
  
  client.connect(mqttServer)
  client.publish(outTopic, outMessage)

# cleanup aged Noaircraft 
def cleanNoHitAircraft():
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor( "planes/trace", thisFunctionName) 
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
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor( "planes/trace", thisFunctionName) 
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
    global filteredAircraft
    global excludeOperatorList
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor("planes/trace", thisFunctionName)   
    interesting = 'False'
    for p in aircraftSession:
        if( p.aircraftID == aircraftID):
            icaohex =aircraftID 
            owners = p.aircraftOwner
            #operatorFlagCode = p.aircraftOperatorFlagCode
            strICAO = p.aircraftOperatorFlagCode
            strReg = p.aircraftRegistration
            strType =p.aircraftType 
            epochTime =  p.aircraftWhenSeenComputer
            interesting = p.aircraftInteresting
            knownPlane = "True"
            #print("known plane - local DB")
            mqttOutLine = thisFunctionName + " ==> aircraft info provided by session object"
            outPutMQTTnoColor("planes/trace", mqttOutLine)   
            # if (interestingAircraft()):
            #         p.set_Interesting("True")
            #         #p.set_AlertTime(localtimeComputer)
            #         #add the aircraft to the database
            #         #add a seen record
            #         interesting = "True"
            #         mqttOutLine = thisFunctionName + " ==> interestingAircraft classifies as an interesting aircraft: " + aircraftID
            #         outPutMQTTnoColor("planes/trace", mqttOutLine)
            # else:
            #     p.set_Interesting("False")
            #     interesting = "False" 
            #     mqttOutLine = thisFunctionName + " ==> local DB classifies as NOT an interesting aircraft: " + aircraftID
            #     outPutMQTTnoColor("planes/trace", mqttOutLine)

            if (interesting == 'True'):

                    mqttOutLine = thisFunctionName + " ==> local DB classifies as an interesting aircraft: " + aircraftID
                    outPutMQTTnoColor("planes/trace", mqttOutLine)
            else:

                mqttOutLine = thisFunctionName + " ==> local DB classifies as NOT an interesting aircraft: " + aircraftID
                outPutMQTTnoColor("planes/trace", mqttOutLine)   
            
                         
            
            operatorFlagCode = strICAO
            if operatorFlagCode not in excludeOperatorList:        
                    addAircraftDB(aircraftID)  
                    conn = create_connection(database)
                    cur = conn.cursor()
                    epochTime = time.time() 
                    cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);",(icaohex,epochTime ))
                    cur = conn.commit
                    cur = conn.close 
                    #aircraftSession.append(p)
                    mqttOutLine = thisFunctionName + " ==> UNFILTERED  operator: " + operatorFlagCode
                    outPutMQTTnoColor("planes/trace", mqttOutLine)
                    #outPutAircraft()
                    
            else:
                 filteredAircraft = filteredAircraft +1  
                 mqttOutLine = thisFunctionName + " ==> FILTERED operator: " + operatorFlagCode
                 outPutMQTTnoColor("planes/trace", mqttOutLine)           
            return True
    mqttOutLine = thisFunctionName + " ==> aircraft info not in session object: " + aircraftID
    outPutMQTTnoColor("planes/trace", mqttOutLine)             
    return False

# return the index of the aircraft 
def returnPlaneIndex(aircraftID):
    global aircraftSession
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor("planes/trace", thisFunctionName)   
    count = 0
    for p in aircraftSession:
        if( p.aircraftID == aircraftID):
            return count
        count = count + 1
    return -1 

# see if we have already failed to find info on the aircraft 
def isKnownNoHitCheck(aircraftID):
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor("planes/trace", thisFunctionName)     
    for p in noHitSession:
        if( p.noHitID == aircraftID):
            #print("known no hit")
            mqttOutLine = thisFunctionName + " ==> aircraft is kown to not return data from webservice"
            outPutMQTTnoColor("planes/trace", mqttOutLine)
            return True
    return False

# add an aircraft to the list used during the session
def addNoHit(aircraftID):
 
    p = noHit(str(aircraftID))
    localtime = time.asctime( time.localtime(time.time()) )
    localtimeComputer = datetime.today()
    p.set_noHitWhenSeen(str(localtime))
    p.set_noHitWhenSeenComputer(localtimeComputer)
    noHitSession.append(p)
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor("planes/trace", mqttOutLine)
# and records to DB when interesting aircraft identified


def addAircraftDB(icaohex):
  thisFunctionName = sys._getframe(  ).f_code.co_name
  outPutMQTTnoColor( "planes/trace", thisFunctionName) 
  if (not isKnownPlaneDB(str(icaohex))):
        conn = create_connection(database)
        cur = conn.cursor()
        epochTime = time.time() 
        cur.execute("INSERT INTO AIRCRAFT VALUES(?,?,?,?,?,?,?);",(icaohex, owners, strICAO, strReg, strType, epochTime, interesting ))
       # cur.execute("INSERT INTO AIRCRAFT VALUES('icaohex2','2','3','4','5', 6);")
        #print("unknown plane - adding  aircraft row") 
        cur = conn.commit
        cur = conn.close  
        outPutMQTTnoColor( "planes/trace", thisFunctionName + "   added plane to local db: " + strICAO + " " +owners)  
  else:
        outPutMQTTnoColor( "planes/trace", thisFunctionName + "   plane already in local db: " + strICAO + " " +owners)
       
#add an aircraft to the session object
def outPutAircraft():
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor("planes/trace", thisFunctionName)   
    global mqttOutColor
    global alertCount 
    global filteredAircraft
    adsbExchangeBaseFull = adsbExchangeBase + str(icaohex) 
    itemNum = returnPlaneIndex(str(icaohex))
    outcolor= setOutcolor
    mqttOutColor = "TFT_WHITE"
    minutes = 0 
    if (str(aircraftSession[itemNum].get_aircraftID()[0:1]) != 'a'):
        mqttOutColor = "TFT_GOLD"      
       
    if (str(aircraftSession[itemNum].get_Interesting()) == 'True'):
        outcolor="green"
        mqttOutColor = "TFT_GREEN"  
        timeSince = datetime.today() - aircraftSession[itemNum].get_AlertTime() 
        minutes = timeSince.total_seconds() / 60

        if ((aircraftSession[itemNum].get_AlertTime()) == aircraftSession[itemNum].get_WhenSeenComputer() or minutes > 15):
            outcolor="yellow" 
            mqttOutColor = "TFT_YELLOW"  
            localtimeComputer = datetime.today()
            aircraftSession[itemNum].set_AlertTime(localtimeComputer)
            #mqout = str(aircraftSession[itemNum].get_Registration())  + " " + str(aircraftSession[itemNum].get_Owner()) +"  " + str(aircraftSession[itemNum].get_Type()) 
            mqout =  str(aircraftSession[itemNum].get_Owner()) +". " + str(aircraftSession[itemNum].get_Type()) 
            localtime = time.asctime( time.localtime(time.time()) )
            mqout2 = localtime  + " " + str(aircraftSession[itemNum].get_Registration())  + " " + str(aircraftSession[itemNum].get_Owner()) +"  " + str(aircraftSession[itemNum].get_Type() +"  " + adsbExchangeBaseFull) 
            outPutMQTTnoColor("planes/watchfor", mqout) 
            outPutMQTTnoColor("planes/watchforLong", mqout2) 
            alertCount  += 1
            outPutMQTTnoColor("planes/alerts", str(alertCount)) 
            conn = create_connection(database)
            cur = conn.cursor()
            epochTime = time.time() 
            cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);",(icaohex,epochTime ))
            cur = conn.commit
            cur = conn.close             
    #outLine = time.asctime(time.localtime(time.time()))+ " | " + str(aircraftSession[itemNum].get_WhenSeen()) + " | " + str(aircraftSession[itemNum].get_aircraftID())+ " | "+ str(aircraftSession[itemNum].get_Registration())  + " | " + str(aircraftSession[itemNum].get_Owner())+ " | " + str(aircraftSession[itemNum].get_OperatorFlagCode()) + " | " + str(aircraftSession[itemNum].get_Type() + " | " +  dataSource + " | " + adsbExchangeBaseFull) 
    
    #outLine = dataSource + " | " +  str(aircraftSession[itemNum].get_aircraftID())+ " | "+ str(aircraftSession[itemNum].get_Registration())  + " | " + str(aircraftSession[itemNum].get_Owner())+ " | " + str(aircraftSession[itemNum].get_OperatorFlagCode()) + " | " + str(aircraftSession[itemNum].get_Type() + " | " +  adsbExchangeBaseFull) 

    if str(aircraftSession[itemNum].get_OperatorFlagCode()) not in excludeOperatorList:        
        outLine = str(aircraftSession[itemNum].get_aircraftID())+ " | "+ str(aircraftSession[itemNum].get_Registration())  + " | " + str(aircraftSession[itemNum].get_Owner())+ " | " + str(aircraftSession[itemNum].get_OperatorFlagCode()) + " | " + str(aircraftSession[itemNum].get_Type() + " | " +  adsbExchangeBaseFull) 
 
        print(outLine)   
        mqttOutLine = str(aircraftSession[itemNum].get_aircraftID()) + " "+ str(aircraftSession[itemNum].get_Registration()) + " " + str(aircraftSession[itemNum].get_Owner())+ " " + str(aircraftSession[itemNum].get_OperatorFlagCode()) + " " + str(aircraftSession[itemNum].get_Type())
        outPutMQTT(mqttOutColor, "planes/console", mqttOutLine) 
        mqttOutLine = thisFunctionName + " ==> outputting plane information: " + str(aircraftSession[itemNum].get_aircraftID())    
    else:
            filteredAircraft = filteredAircraft +1  
            mqttOutLine = thisFunctionName + " ==> filtered operator: " + str(aircraftSession[itemNum].get_aircraftID())
                       



    # outLine = str(aircraftSession[itemNum].get_aircraftID())+ " | "+ str(aircraftSession[itemNum].get_Registration())  + " | " + str(aircraftSession[itemNum].get_Owner())+ " | " + str(aircraftSession[itemNum].get_OperatorFlagCode()) + " | " + str(aircraftSession[itemNum].get_Type() + " | " +  adsbExchangeBaseFull) 
 
    # print(outLine)   
    # mqttOutLine = str(aircraftSession[itemNum].get_aircraftID()) + " "+ str(aircraftSession[itemNum].get_Registration()) + " " + str(aircraftSession[itemNum].get_Owner())+ " " + str(aircraftSession[itemNum].get_OperatorFlagCode()) + " " + str(aircraftSession[itemNum].get_Type())


    outPutMQTTnoColor("planes/trace", mqttOutLine) 
                            
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
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor( "planes/trace", thisFunctionName) 


   

    p = Aircraft(aircraftID)
    p.set_Registration(strReg)
    p.set_OperatorFlagCode(strICAO)
    p.set_Type(strType)
    p.set_Owner(owners)
    localtime = time.asctime( time.localtime(time.time()) )
    localtimeComputer = datetime.today()
    p.set_WhenSeen(str(localtime))
    p.set_WhenSeenComputer(localtimeComputer)

    
    
    #need to make sure that we have values in the AlertTime
    #seting back in the event it is an interesting plane to get alert when first seen.
    myDatetime = datetime.today()  
    myFakeAlertTime = myDatetime - timedelta(minutes = 20) 
    p.set_AlertTime(localtimeComputer)

# going to add a column to table  AIRCRAFTINTERSTING -- moving to one aircraft DB 
    if (interestingAircraft()):
        p.set_Interesting("True")
        #add the aircraft to the database
        #add a seen record
        interesting = "True"
        mqttOutLine = thisFunctionName + " ==> local DB classifies as an interesting aircraft: " + aircraftID
        outPutMQTTnoColor("planes/trace", mqttOutLine)
    else:
        p.set_Interesting("False")
        interesting = "False" 
        mqttOutLine = thisFunctionName + " ==> local DB classifies as NOT an interesting aircraft: " + aircraftID
        outPutMQTTnoColor("planes/trace", mqttOutLine)
    
    mqttOutLine = thisFunctionName + " ==> adding aircraft to session object: " + aircraftID
    outPutMQTTnoColor("planes/trace", mqttOutLine)  
    aircraftSession.append(p)
  
    if strICAO not in excludeOperatorList:        
            addAircraftDB(aircraftID)  
            conn = create_connection(database)
            cur = conn.cursor()
            epochTime = time.time() 
            cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);",(icaohex,epochTime ))
            cur = conn.commit
            cur = conn.close 
            #aircraftSession.append(p)
            mqttOutLine = thisFunctionName + " ==> potentially interesting operator: " + strICAO
            outPutMQTTnoColor("planes/trace", mqttOutLine)
            #outPutAircraft()
            
    else:
         filteredAircraft = filteredAircraft +1  
         mqttOutLine = thisFunctionName + " ==> filtered operator: " + strICAO
         outPutMQTTnoColor("planes/trace", mqttOutLine) 
#    return

#is this an aircraft we are interested in 

def interestingAircraft():
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor("planes/trace", thisFunctionName)   
    #owners=icao_data['RegisteredOwners']
    #strICAO = str(icao_data['OperatorFlagCod
    #strReg = str(icao_data['Registration'])
    global interestingAircraftCount 
    interestCount = 0
    o= 0
    while o < len(watchlistOwner):
        if watchlistOwner[o].lower() in owners.lower():
            interestCount += 1
            mqttOutLine = thisFunctionName + " ==> interesting owner"
            outPutMQTTnoColor("planes/trace", mqttOutLine)
        o += 1

    if strICAO in watchICAO:
        interestCount += 1
        mqttOutLine = thisFunctionName + " ==> interesting operator" 
        outPutMQTTnoColor("planes/trace", mqttOutLine)       

    if strReg in watchReg:
        interestCount += 1
        mqttOutLine = thisFunctionName + " ==> interesting tail number"
        outPutMQTTnoColor("planes/trace", mqttOutLine)

    if interestCount > 0:
       interestingAircraftCount  += 1
       outPutMQTTnoColor("planes/interestingAircraft", str(interestingAircraftCount))
       mqttOutLine = thisFunctionName + " ==> determined to be interesting aircraft" 
       outPutMQTTnoColor("planes/trace", mqttOutLine)      
       return True
       
    else:
        mqttOutLine = thisFunctionName + " ==> determined NOT to be interesting aircraft"
        outPutMQTTnoColor("planes/trace", mqttOutLine)
        return False

##-----------------------------------------------------------------------------------------------------------------------------###
## this is DB interaction code





def create_connection(db_file):
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor("planes/trace", thisFunctionName)   
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
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor("planes/trace", thisFunctionName)   
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
        #operatorFlagCode =row[2]
        strICAO = row[2]
        strReg =row[3]
        strType =row[4]
        epochTime =row[5]
        interesting =row[6]
        knownPlane = "True"
        
        #strICAO = str(operatorFlagCode)
        strAircraftID = str(aircraftID)
        p = Aircraft(str(aircraftID))
        p.set_Registration( strReg)
        p.set_OperatorFlagCode(strICAO)
        p.set_Type(strType)
        p.set_Owner(owners)
        localtime = time.asctime( time.localtime(time.time()) )
        localtimeComputer = datetime.today()
        p.set_WhenSeen(str(localtime))
        p.set_WhenSeenComputer(localtimeComputer)
        p.set_Interesting(interesting)

        mqttOutLine = thisFunctionName + " ==> aircraft info provided by LOCALDB: " + aircraftID
        outPutMQTTnoColor("planes/trace", mqttOutLine) 

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
            #print("known adding sighting info")
        else:
            p.set_Interesting("False")
            p.set_AlertTime(localtimeComputer)
            interesting = "False" 

        aircraftSession.append(p)
        #outPutAircraft()
        return True
    
    mqttOutLine = thisFunctionName + " ==> aircraft info NOT in LOCALDB: " + aircraftID
    outPutMQTTnoColor("planes/trace", mqttOutLine) 
    return False    
    
###
def checkFAA(aircraftID):
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor("planes/trace", thisFunctionName)   
    global knownPlane
# create a database connection
    conn = create_connection(database)
    cur = conn.cursor()
    aircraftIDq = aircraftID + "%"
    cur.execute("SELECT * FROM MASTER WHERE AIRCRAFTID =?;", (aircraftID,))

    rows = cur.fetchall()
    cur.close 

    for row in rows:
        #print("info avail locally")

        icaohex =row[2]
        owners =row[1]
        operatorFlagCode ="xxx"
        strReg ="N" + row[0]
        strType ="xxx"
        epochTime = datetime.today()
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
        localtimeComputer = datetime.today()
        p.set_WhenSeen(str(localtime))
        p.set_WhenSeenComputer(localtimeComputer)
        p.set_Interesting(interesting)
      
        mqttOutLine = thisFunctionName + " ==> aircraft info provided by LOCAL FAADB: " + aircraftID
        outPutMQTTnoColor("planes/trace", mqttOutLine) 
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
        #outPutAircraft()
        return True
    mqttOutLine = thisFunctionName + " ==> aircraft info NOT in LOCAL FAADB: " + aircraftID
    outPutMQTTnoColor("planes/trace", mqttOutLine)       
    return False 
###  

def dbKnownNoHit(aircraftID):
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor("planes/trace", thisFunctionName)     

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
    thisFunctionName = sys._getframe(  ).f_code.co_name
    outPutMQTTnoColor("planes/trace", thisFunctionName)     

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
    mqttOutLine = thisFunctionName + " ==> added new known no info aircraft: " + aircraftID
    outPutMQTTnoColor("planes/trace", mqttOutLine)   
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
global alertCount
global watchlistOwner
global watchReg
global watchICAO
global interestingAircraftCount

sampling_period =60
sampling_period_seconds = int(sampling_period)

excludeOperatorList="LXJ,AAL,ASA,UAL,SWA,FFT,SKW,WJA,FLE,ASH,DAL,ENY,NKS,VOI,JBU,WSW,UPS,SWQ,ABX,FDX,QXE,SLI,EJA,JZA,ROU,GAJ,FDY,CFS,NJAS"
watchlistOwner= ["Aces","ACES","Missile Defense Agency","NASCAR", "Motorsports","Federal", "United States", "Oprah", "Police", "State Farm", "Sherrif", "Arizona Department", "NASA", "Air Force", "Museum", "Google", "Apple", "Penske" , "Cardinals" , "Stewart-Haas" , "Tanker"]
watchReg="N44SF,N812LE,N353P,N781MM,N88WR,N383LS,N78HV,N4DP,N9165H,N519JG,N280NV"
watchICAO="F16,S211,BE18,AJET,KMAX,HGT,ST75,RRR,MRF1,L1P,T6,BGR,TNK,P4Y,A4"

database = "/fr24db/aircraftMon.db" 
#database = "/home/beed2112/fr24db/aircraftMon.db"   #local 


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



#lastCleanupTimeAircraft = datetime.today()
lastCleanupTimeAircraft = datetime.today()
purgeMinutesAircraft = 240

thisFunctionName = "mainLine Startup"
outPutMQTTnoColor( "planes/trace", thisFunctionName) 
# grab aircraft.json from the reciever

receiver_url ='http://192.168.0.116'
#receiver_url ='http://192.168.0.55:8080' 
adsbExchangeBase = 'https://globe.adsbexchange.com/?icao='
while True:
  thisFunctionName = sys._getframe(  ).f_code.co_name + "forever while loop startup ++++++++++++++++++++++++++++++++++++++++"
  outPutMQTTnoColor("planes/trace", thisFunctionName)   
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
      thisFunctionName = " ==> success retrieving aircraft.json"
      outPutMQTTnoColor("planes/trace", thisFunctionName)        
      aircraftCount= info_data['aircraft_count']
  except:
      aircraftCount= 0
      thisFunctionName = " ==> FAILURE retrieving aircraft.json"
      outPutMQTTnoColor("planes/trace", thisFunctionName)     

  totalAircraftCount = totalAircraftCount + aircraftCount
  currentTime = time.localtime()
  currentHour = currentTime.tm_hour
  currentMinute = currentTime.tm_hour
  mtCurrentTime = " " 
  myCurrentTime = str(currentHour) + ":" + str(currentMinute) 
  mqttLine1 =  "+++--Curr " + myCurrentTime
  part1 =  "+++" 
  part2 =  "-- Strt " + myCurrentTime + "--tot seen " + str(totalAircraftCount) + "-- cur " + str(aircraftCount) + "-- flt " + str(filteredAircraft)
  mqttLine2 =  "--tot seen " + str(totalAircraftCount) + "-- cur " + str(aircraftCount)
  part4 = "--wsCall " + str(webserviceCalls) + "--wsErr " + str(webServiceError)
  part5 = "--knwnNoHit " + str(knownNoHitDB) +  "--nohit " + str(nohit) + "--lclDB " + str(localResolve)
  part6 = "lclMem " + str(localMemResolve) + "--+++"
  #outline = part1 + part2 + "--" + part3 + "--" + "--"+ part4 + part5 +  "--"  + part6
  outline =  part1 + part2 +  "--" + part4 + "--" + part5 +  "--"  + part6
  print (outline) 

  mqttOutColor =  "TFT_ORANGE" 
  mqttOutLine = mqttLine1 + mqttLine2 
  outPutMQTT(mqttOutColor, "planes/console", mqttOutLine) 


#loop thru the aircraft 
  i = 00
  
  while i < aircraftCount:
   iPrint = i + 1 
   icaohex = aircraft_data['aircraft'][i]['hex']
   thisFunctionName = "aircraft processing loop STARTS " + str(aircraftCount) + " aircraft processing #" + str(iPrint) + " ==> " + icaohex
   outPutMQTTnoColor("planes/trace", thisFunctionName)    
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
      #addAircraft(icaohex)
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
                        thisFunctionName = sys._getframe(  ).f_code.co_name + " ==> aircraft info provided be WEBSERVICE            " + icaohex
                        outPutMQTTnoColor("planes/trace", thisFunctionName)                          
                        addAircraft(icaohex)
                        outPutAircraft()
                        
                    else:
                            addNoHit(icaohex)
                            nohit += 1
                            if (checkFAA(icaohex)):
                                thisFunctionName = " ==> aircraft info provided by FAA database" 
                                outPutMQTTnoColor("planes/trace", thisFunctionName)    
                            else:  
                                mqttOutLine =  icaohex + " " + str(nohit) 
                                outPutMQTTnoColor("planes/nohit", mqttOutLine)
                                addIfNewNoHit(icaohex)    
                            
                except (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, Exception) as e: 
                    strICAO = "ERROR"
                    webServiceError += 1
                    print(e)
                    thisFunctionName = " ==> webservice error" 
                    outPutMQTTnoColor("planes/trace", thisFunctionName)
        else:
            knownNoHitDB += 1
            thisFunctionName = " ==> we know we can't find information on this aircraft" 
            outPutMQTTnoColor("planes/trace", thisFunctionName)          

   timeSinceLastCleanupAircraft = datetime.today() - lastCleanupTimeAircraft
   minutesSinceLastCleanupAircraft = timeSinceLastCleanupAircraft.total_seconds() / 60

   if (minutesSinceLastCleanupAircraft> purgeMinutesAircraft):
       #cleanAircraft()
       lastCleanupTimeAircraft = datetime.today()
       hold1 = len(aircraftSession)
       cleanAircraft()
       hold2 = len(aircraftSession)
       outLine = time.asctime(time.localtime(time.time()))+ " | Aircraft memory clean up time before " + str(hold1) + " | after " + str(hold2) 
       outcolor = "blue"
       #print(colored(outLine, outcolor)) 
       print(outline)
       thisFunctionName = outline 
       outPutMQTTnoColor("planes/trace", thisFunctionName)     
       #aircraftSession = []
       hold1 = len(noHitSession)
       cleanNoHitAircraft()
       hold2 = len(noHitSession)
       outLine = time.asctime(time.localtime(time.time()))+ " | noHit memory clean up time before " + str(hold1) + " | after " + str(hold2) 
       outcolor = "yellow"
       #print(colored(outLine, outcolor)) 
       print(outLine)
       thisFunctionName = outline 
       outPutMQTTnoColor("planes/trace", thisFunctionName)      

   thisFunctionName = "processing loop     ==> " 
   outPutMQTTnoColor("planes/trace", thisFunctionName + "COMPLETED processing aircraft: " + icaohex ) 

  thisFunctionName = sys._getframe(  ).f_code.co_name + "aircraft processing loop ENDS           " 
  outPutMQTTnoColor("planes/trace", thisFunctionName)  
  thisFunctionName = "sleeping........................" 
  outPutMQTTnoColor("planes/trace", thisFunctionName)        
  myCount = 0  
  

  for  myCount in range(sampling_period_seconds):
   print(".",end="")
   time.sleep(1) 
   myCount += 1   
  print("")


  
   








# no code below here 

# dealing with time   https://thispointer.com/how-to-add-minutes-to-datetime-in-python/

# https://globe.adsbexchange.com/?icao=aa8ef0
# aa43ee | N7600P | SAS Institute Inc | F9EX | Falcon 900EX EASy    z
