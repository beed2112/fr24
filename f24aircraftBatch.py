import sys
import os
import json
import time

import requests
from termcolor import colored


# device_id = os.getenv('DEVICE_ID')
# if not device_id:
#   raise ValueError('DEVICE_ID env variable is not set')

# receiver_url = os.getenv('RECEIVER_URL')
# if not receiver_url:
#   raise ValueError('RECEIVER_URL env variable is not set')

# output_bucket = os.getenv('OUTPUT_BUCKET')
# if not output_bucket:
#   raise ValueError('OUTPUT_BUCKET env variable is not set')

# sampling_period_seconds = os.getenv('SAMPLING_PERIOD_SECONDS')
# if not sampling_period_seconds:
#   raise ValueError('SAMPLING_PERIOD_SECONDS env variable is not set')
sampling_period =60

sampling_period_seconds = int(sampling_period)

excludeList="AAL,ASA,UAL,SWA,FFT,SKW,WJA,FLE,AAY,ASH,DAL,ENY,NKS"
watchlistOwner= ["Prime Air", "United States", "Utah Trustee", "Police", "Police", "State Farm", "Sherrif"]
watchReg="N44SF,N812LE"
watchICAO="F16,S211,BE18,AJET,KMAX,HGT"



getIt=sys.argv[1]
#getIt="history_0.json"
# bucket = client.get_bucket(output_bucket)
x=0
receiver_url ='http://192.168.0.116'
#while True
while x < 1:

  r = requests.get(f'{receiver_url}/dump1090/{getIt}')
  #r = requests.get(f'{receiver_url}/dump1090/data/aircraft.json')

  if r.status_code != 200:
    raise ValueError(f'ERROR: getting aircraft json data :{r.text}')

  aircraft_data = r.json()

  now = aircraft_data['now']
  info_data = {
    'now': now,
    'aircraft_count' : len(aircraft_data['aircraft']),
    'messages': aircraft_data['messages']
  }
  print ("+++------------------------------------------------------------------------------------------------------+++", getIt)
 # print('INFO: ' + json.dumps(info_data))


#{"hex":"c070d7"
# "squawk":"4314"
# "flight":"CHETA71 ",
# "lat":33.454926,
# "lon":-111.886469,
# "nucp":7,
# "seen_pos":16.6,
# "altitude":15950,
# "vert_rate":0,
# "track":281,
# "speed":282,
# "category":"A1",# "mlat":[],
# "tisb":

#print(icaohex, "|", icao_data['Registration'], "|", icao_data['ICAOTypeCode'], "|", icao_data['OperatorFlagCode'], "|", icao_data['RegisteredOwners'], "|", icao_data['Type'])
#nan    |168067   | C30J | C30J | United States Marine Corps KC-130J Hercules
#ae4be3 | 10-5716 | C30J | C30J | United States Air Force | HC-130J Hercules 
#a1c2c4 | N212UT | S211 | S211 | Flight Research Inc | S.211
#ab9b84 | N847TA | F16 | F16 | Top Aces Inc | F-16B Netz
#ae4be3 | 10-5716 | C30J | C30J | United States Air Force | HC-130J Hercules 

  i = 00
  while i < info_data['aircraft_count']:
   icaohex = aircraft_data['aircraft'][i]['hex']
   icao_response = requests.get(f'https://hexdb.io/api/v1/aircraft/{icaohex}')

   icao_data = icao_response.json()

   if icao_response.status_code == 200:
       if icao_data['OperatorFlagCode'] not in excludeList:
         localtime = time.asctime( time.localtime(time.time()) )
         owners=icao_data['RegisteredOwners']
         
         outcolor="white"


         o= 0
         while o < len(watchlistOwner):
            if watchlistOwner[o] in owners:
                outcolor="green" 
            o += 1
                

         icao_data['Registration']         
         
       
         if icao_data['OperatorFlagCode']  in watchICAO or icao_data['Registration'] in watchReg:
           outcolor="yellow"
  
        
         outLine=str(localtime) +" | " + str(icaohex)+ " | "+ str(icao_data['Registration'])+ " | "+ str(icao_data['ICAOTypeCode'])+ " | "+ str(icao_data['OperatorFlagCode'])+ " | "+ str(icao_data['RegisteredOwners'])+ " | "+ str(icao_data['Type'])
         print(colored(outLine, outcolor))
 
   i += 1


  
  #time.sleep(sampling_period)
  x=1




