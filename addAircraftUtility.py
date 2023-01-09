
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
def create_connection(db_file):
  
    conn = None
    try:
        conn = sqlite3.connect(db_file , isolation_level = None)
    except Error as e:
        print(e)

    return conn

#('a2d458', 'unknown-owner', 'L1P', 'N2812H', '1944 North American T-6 Texan','1673281178.0664');

database = "aircraftMon.db" 
conn = create_connection(database)
cur = conn.cursor()
icaohex= 'a2d458'
owners = 'unknown-owner'
strICAO= 'L1P'
strReg= 'N2812H'
strType = '1944 North American T-6 Texan'


epochTime = time.time() 
cur.execute("INSERT INTO AIRCRAFT VALUES(?,?,?,?,?,?);",(icaohex, owners, strICAO, strReg, strType, epochTime ))
#cur.execute("INSERT INTO AIRCRAFT VALUES('icaohex2','2','3','4','5', 6);")
cur = conn.commit
cur = conn.close 