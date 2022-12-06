import sys
import os
import json
import time

import requests



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

# client = storage.Client()

# bucket = client.get_bucket(output_bucket)

receiver_url ='http://192.168.0.116'
while True:
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

  #aircraft_data['aircraft'][00]
#loop aircraft keys count starts at 0  while lt aircraft count 
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
# "category":"A1",
# "mlat":[],
# "tisb":

  i = 00
  while i < info_data['aircraft_count']:
   callsignin = aircraft_data['aircraft'][i]['hex']
   callsign = requests.get(f'https://hexdb.io/api/v1/aircraft/{callsignin}')

   if callsign.status_code == 200:
     print(callsign.text)
    #raise ValueError(f'ERROR: getting data from hexdb.io:{callsign.text}')  
   #print(callsign['text']['Registration'], callsign['text']['ICAOTypeCode'], callsign['text']['OperatorFlagCode'], callsign['text']['RegisteredOwners'], callsign['text']['Type'])
   
   #print(callsign['text'])
#    if "flight" in  aircraft_data['aircraft'][i]:  
#     print(aircraft_data['aircraft'][i]['hex'], aircraft_data['aircraft'][i]['flight'])
#    else:
#     print(aircraft_data['aircraft'][i]['hex'])
   i += 1


  print('INFO: ' + json.dumps(info_data))

#   file_name = f'{device_id}/{now}.json'

#   blob = Blob(file_name, bucket)
#   blob.upload_from_string(json.dumps(aircraft_data), content_type='application/json')

#  print(f'INFO: Uploaded : {file_name}')
  
  time.sleep(sampling_period)






