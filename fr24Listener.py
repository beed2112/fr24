import sys
import os
import json
import time
import paho.mqtt.client as paho
import datetime
import requests
from termcolor import colored
import sqlite3
from sqlite3 import Error
from aircraft import Aircraft
from nohitAircraft import noHit
from datetime import datetime, timedelta  



def output_mqtt(out_color, out_topic, out_message):
    mqtt_server = "mqtt"
    mqtt_user = "me"
    mqtt_pass = "me"
    mqtt_outline = f"{out_color}|{out_message}"

    client = paho.Client()
    client.username_pw_set(mqtt_user, mqtt_pass)
    client.connect(mqtt_server)
    client.publish(out_topic, mqtt_outline)


def output_mqtt_no_color(out_topic, out_message):
    mqtt_server = "mqtt"
    mqtt_user = "me"
    mqtt_pass = "me"

    client = paho.Client()
    client.username_pw_set(mqtt_user, mqtt_pass)
    client.connect(mqtt_server)
    client.publish(out_topic, out_message)


def clean_no_hit_aircraft():
    this_function_name = sys._getframe().f_code.co_name
    output_mqtt_no_color("planes/trace", this_function_name)
    count = 0
    for p in no_hit_session:
        age = last_cleanup_time_aircraft - p.noHitWhenSeenComputer
        age_minutes = age.total_seconds() / 60
        if age_minutes > purge_minutes_aircraft:
            no_hit_session.pop(count)
        count += 1
    return


def clean_aircraft():
    this_function_name = sys._getframe().f_code.co_name
    output_mqtt_no_color("planes/trace", this_function_name)
    count = 0
    for p in aircraft_session:
        age = last_cleanup_time_aircraft - p.aircraftWhenSeenComputer
        age_minutes = age.total_seconds() / 60
        if age_minutes > purge_minutes_aircraft:
            aircraft_session.pop(count)
        count += 1
    return


def is_filtered_operator():
    global str_icao, aircraft_id
    operator_flag_code = str_icao
    if operator_flag_code not in exclude_operator_list:
        add_aircraft_db(aircraft_id)
        conn = create_connection(database)
        cur = conn.cursor()
        epoch_time = time.time()
        cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);", (icaohex, epoch_time))
        conn.commit()
        conn.close()
        mqtt_outline = f"{this_function_name} ==> UNFILTERED operator: {operator_flag_code}"
        output_mqtt_no_color("planes/trace", mqtt_outline)
    else:
        global filtered_aircraft
        filtered_aircraft += 1
        mqtt_outline = f"{this_function_name} ==> FILTERED operator: {operator_flag_code}"
        output_mqtt_no_color("planes/trace", mqtt_outline)
    return True


def is_known_plane(aircraft_id):
    global aircraft_session, filtered_aircraft, exclude_operator_list, str_icao
    this_function_name = sys._getframe().f_code.co_name
    output_mqtt_no_color("planes/trace", this_function_name)
    for p in aircraft_session:
        if p.aircraftID == aircraft_id:
            global icaohex, owners, str_reg, str_type, epoch_time, interesting, known_plane
            icaohex = aircraft_id
            owners = p.aircraftOwner
            str_icao = p.aircraftOperatorFlagCode
            str_reg = p.aircraftRegistration
            str_type = p.aircraftType
            epoch_time = p.aircraftWhenSeenComputer
            interesting = p.aircraftInteresting
            known_plane = "True"
            mqtt_outline = f"{this_function_name} ==> aircraft info provided by session object"
            output_mqtt_no_color("planes/trace", mqtt_outline)

            if interesting == 'True':
                mqtt_outline = f"{this_function_name} ==> memory object classifies as an interesting aircraft: {aircraft_id}"
            else:
                mqtt_outline = f"{this_function_name} ==> memory object classifies as NOT an interesting aircraft: {aircraft_id}"
            output_mqtt_no_color("planes/trace", mqtt_outline)
            return True
    mqtt_outline = f"{this_function_name} ==> aircraft info not in session object: {aircraft_id}"
    output_mqtt_no_color("planes/trace", mqtt_outline)
    return False


def return_plane_index(aircraft_id):
    global aircraft_session
    this_function_name = sys._getframe().f_code.co_name
    output_mqtt_no_color("planes/trace", this_function_name)
    for count, p in enumerate(aircraft_session):
        if p.aircraftID == aircraft_id:
            mqtt_outline = f"{this_function_name} GOOD returning index for found aircraft in session object {aircraft_id}"
            output_mqtt_no_color("planes/trace", mqtt_outline)
            return count
    mqtt_outline = f"{this_function_name} BAD returning index for unfound aircraft in session object {aircraft_id}"
    output_mqtt_no_color("planes/trace", mqtt_outline)
    return -1


def is_known_no_hit_check(aircraft_id):
    this_function_name = sys._getframe().f_code.co_name
    output_mqtt_no_color("planes/trace", this_function_name)
    for p in no_hit_session:
        if p.noHitID == aircraft_id:
            mqtt_outline = f"{this_function_name} ==> aircraft is known to not return data from web service"
            output_mqtt_no_color("planes/trace", mqtt_outline)
            return True
    return False


def add_no_hit(aircraft_id):
    p = noHit(str(aircraft_id))
    localtime_computer = datetime.today()
    p.set_noHitWhenSeen(str(localtime_computer))
    p.set_noHitWhenSeenComputer(localtime_computer)
    no_hit_session.append(p)
    this_function_name = sys._getframe().f_code.co_name
    mqtt_outline = f"{this_function_name} ==> added aircraft to noHit session: {aircraft_id}"
    output_mqtt_no_color("planes/trace", mqtt_outline)


def add_aircraft_db(icaohex):
    this_function_name = sys._getframe().f_code.co_name
    output_mqtt_no_color("planes/trace", this_function_name)
    if not is_known_plane_db(str(icaohex)):
        conn = create_connection(database)
        cur = conn.cursor()
        epoch_time = time.time()
        cur.execute("INSERT INTO AIRCRAFT VALUES(?,?,?,?,?,?,?);", (icaohex, owners, str_icao, str_reg, str_type, epoch_time, interesting))
        conn.commit()
        conn.close()
        output_mqtt_no_color("planes/trace", f"{this_function_name} added plane to local db: {str_icao} {owners}")
    else:
        output_mqtt_no_color("planes/trace", f"{this_function_name} plane already in local db: {str_icao} {owners}")


def output_aircraft():
    this_function_name = sys._getframe().f_code.co_name
    output_mqtt_no_color("planes/trace", this_function_name)
    global mqtt_out_color, alert_count, filtered_aircraft, icaohex, str_icao, owners, str_reg, str_type
    adsb_exchange_base_full = adsb_exchange_base + str(icaohex)
    item_num = return_plane_index(str(icaohex))
    outcolor = set_outcolor
    mqtt_out_color = "TFT_WHITE"
    minutes = 0
    if item_num != -1:
        if str(aircraft_session[item_num].get_OperatorFlagCode()) not in exclude_operator_list and str(aircraft_session[item_num].get_Owner()) not in exclude_owner_list:
            if str(aircraft_session[item_num].get_aircraftID()[0:1]) != 'a':
                mqtt_out_color = "TFT_GOLD"

            if str(aircraft_session[item_num].get_Interesting()) == 'True':
                outcolor = "green"
                mqtt_out_color = "TFT_GREEN"
                time_since = datetime.today() - aircraft_session[item_num].get_AlertTime()
                minutes = time_since.total_seconds() / 60
                my_alert_time = aircraft_session[item_num].get_AlertTime()
                my_seen_time = aircraft_session[item_num].get_WhenSeenComputer()

                if my_alert_time == my_seen_time or minutes > 15:
                    outcolor = "yellow"
                    mqtt_out_color = "TFT_YELLOW"
                    localtime_computer = datetime.today()
                    aircraft_session[item_num].set_AlertTime(localtime_computer)
                    mqout = f"{aircraft_session[item_num].get_Owner()}. {aircraft_session[item_num].get_Type()}"
                    localtime = time.asctime(time.localtime(time.time()))
                    mqout2 = f"{localtime} {aircraft_session[item_num].get_Registration()} {aircraft_session[item_num].get_Owner()} {aircraft_session[item_num].get_Type()} {adsb_exchange_base_full}"
                    output_mqtt_no_color("planes/watchfor", mqout)
                    output_mqtt_no_color("planes/watchforLong", mqout2)
                    alert_count += 1
                    output_mqtt_no_color("planes/alerts", str(alert_count))
                    conn = create_connection(database)
                    cur = conn.cursor()
                    epoch_time = time.time()
                    cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);", (icaohex, epoch_time))
                    conn.commit()
                    conn.close()

            outline = f"{aircraft_session[item_num].get_aircraftID()} | {aircraft_session[item_num].get_Registration()} | {aircraft_session[item_num].get_Owner()} | {aircraft_session[item_num].get_OperatorFlagCode()} | {aircraft_session[item_num].get_Type()} | {adsb_exchange_base_full}"
            print(outline)
            mqtt_outline = f"{aircraft_session[item_num].get_aircraftID()} {aircraft_session[item_num].get_Registration()} {aircraft_session[item_num].get_Owner()} {aircraft_session[item_num].get_OperatorFlagCode()} {aircraft_session[item_num].get_Type()}"
            output_mqtt(mqtt_out_color, "planes/console", mqtt_outline)
            mqtt_outline = f"{this_function_name} ==> outputting plane information: {aircraft_session[item_num].get_aircraftID()}"
        else:
            filtered_aircraft += 1
            mqtt_outline = f"{this_function_name} ==> filtered operator: {aircraft_session[item_num].get_OperatorFlagCode()}"
        output_mqtt_no_color("planes/trace", mqtt_outline)


def add_aircraft(aircraft_id):
    global aircraft_session, localtime, interesting_aircraft_count, str_icao, str_reg, str_type, owners, interesting, filtered_aircraft
    this_function_name = sys._getframe().f_code.co_name
    output_mqtt_no_color("planes/trace", this_function_name)

    p = Aircraft(aircraft_id)
    p.set_Registration(str_reg)
    p.set_OperatorFlagCode(str_icao)
    p.set_Type(str_type)
    p.set_Owner(owners)
    localtime = time.asctime(time.localtime(time.time()))
    localtime_computer = datetime.today()
    p.set_WhenSeen(str(localtime))
    p.set_WhenSeenComputer(localtime_computer)

    if interesting_aircraft():
        p.set_Interesting("True")
        interesting = "True"
        mqtt_outline = f"{this_function_name} ==> local DB classifies as an interesting aircraft: {aircraft_id}"
        output_mqtt_no_color("planes/trace", mqtt_outline)
    else:
        p.set_Interesting("False")
        interesting = "False"
        mqtt_outline = f"{this_function_name} ==> local DB classifies as NOT an interesting aircraft: {aircraft_id}"
        output_mqtt_no_color("planes/trace", mqtt_outline)

    mqtt_outline = f"{this_function_name} ==> adding aircraft to session object: {aircraft_id}"
    output_mqtt_no_color("planes/trace", mqtt_outline)
    aircraft_session.append(p)

    if str_icao not in exclude_operator_list:
        add_aircraft_db(aircraft_id)
        conn = create_connection(database)
        cur = conn.cursor()
        epoch_time = time.time()
        cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);", (icaohex, epoch_time))
        conn.commit()
        conn.close()
        mqtt_outline = f"{this_function_name} ==> NOT a FILTERED operator: {str_icao}"
        output_mqtt_no_color("planes/trace", mqtt_outline)
    else:
        filtered_aircraft += 1
        mqtt_outline = f"{this_function_name} ==> FILTERED operator: {str_icao}"
        output_mqtt_no_color("planes/trace", mqtt_outline)


def interesting_aircraft():
    this_function_name = sys._getframe().f_code.co_name
    output_mqtt_no_color("planes/trace", this_function_name)
    global interesting_aircraft_count, str_icao, str_reg, owners
    interest_count = 0
    for owner in watchlist_owner:
        if owner.lower() in owners.lower():
            interest_count += 1
            mqtt_outline = f"{this_function_name} ==> interesting owner"
            output_mqtt_no_color("planes/trace", mqtt_outline)

    if str_icao in watch_icao:
        interest_count += 1
        mqtt_outline = f"{this_function_name} ==> interesting operator"
        output_mqtt_no_color("planes/trace", mqtt_outline)

    if str_reg in watch_reg:
        interest_count += 1
        mqtt_outline = f"{this_function_name} ==> interesting tail number"
        output_mqtt_no_color("planes/trace", mqtt_outline)

    if interest_count > 0:
        interesting_aircraft_count += 1
        output_mqtt_no_color("planes/interestingAircraft", str(interesting_aircraft_count))
        mqtt_outline = f"{this_function_name} ==> determined to be interesting aircraft"
        output_mqtt_no_color("planes/trace", mqtt_outline)
        return True
    else:
        mqtt_outline = f"{this_function_name} ==> determined NOT to be interesting aircraft"
        output_mqtt_no_color("planes/trace", mqtt_outline)
        return False


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file, isolation_level=None)
    except Error as e:
        print(e)
    return conn


def is_known_plane_db(aircraft_id):
    this_function_name = sys._getframe().f_code.co_name
    output_mqtt_no_color("planes/trace", this_function_name)
    global known_plane, str_icao, owners, str_reg, str_type, epoch_time, interesting
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT * FROM AIRCRAFT WHERE AIRCRAFTID=?;", (aircraft_id,))
    rows = cur.fetchall()
    cur.close()

    for row in rows:
        icaohex = row[0]
        owners = row[1]
        str_icao = row[2]
        str_reg = row[3]
        str_type = row[4]
        epoch_time = row[5]
        interesting = row[6]
        known_plane = "True"
        p = Aircraft(str(aircraft_id))
        p.set_Registration(str_reg)
        p.set_OperatorFlagCode(str_icao)
        p.set_Type(str_type)
        p.set_Owner(owners)
        localtime_computer = datetime.today()
        p.set_WhenSeenComputer(localtime_computer)
        p.set_Interesting(interesting)

        mqtt_outline = f"{this_function_name} ==> aircraft info provided by LOCALDB: {aircraft_id}"
        output_mqtt_no_color("planes/trace", mqtt_outline)

        if interesting_aircraft():
            p.set_Interesting("True")
            p.set_AlertTime(localtime_computer)
        else:
            p.set_Interesting("False")

        if interesting == "True":
            p.set_AlertTime(localtime_computer)
            conn = create_connection(database)
            cur = conn.cursor()
            epoch_time = time.time()
            cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);", (icaohex, epoch_time))
            conn.commit()
            conn.close()
        else:
            p.set_Interesting("False")
            p.set_AlertTime(localtime_computer)

        aircraft_session.append(p)
        return True

    mqtt_outline = f"{this_function_name} ==> aircraft info NOT in LOCALDB: {aircraft_id}"
    output_mqtt_no_color("planes/trace", mqtt_outline)
    return False


def check_faa(aircraft_id):
    this_function_name = sys._getframe().f_code.co_name
    output_mqtt_no_color("planes/trace", this_function_name)
    global known_plane
    conn = create_connection(database)
    cur = conn.cursor()
    aircraft_id_q = f"{aircraft_id}%"
    cur.execute("SELECT * FROM MASTER WHERE AIRCRAFTID =?;", (aircraft_id,))
    rows = cur.fetchall()
    cur.close()

    for row in rows:
        icaohex = row[2]
        owners = row[1].rstrip()
        str_reg = f"N{row[0]}"
        str_type = "xxx"
        interesting = "False"
        known_plane = "True"
        str_icao = "xxx"
        p = Aircraft(str(aircraft_id))
        p.set_Registration(str_reg)
        p.set_OperatorFlagCode(str_icao)
        p.set_Type(str_type)
        p.set_Owner(owners)
        localtime_computer = datetime.today()
        p.set_WhenSeenComputer(localtime_computer)
        p.set_Interesting(interesting)

        mqtt_outline = f"{this_function_name} ==> aircraft info provided by LOCAL FAADB: {aircraft_id}"
        output_mqtt_no_color("planes/trace", mqtt_outline)

        if interesting == "True":
            p.set_AlertTime(localtime_computer)
            conn = create_connection(database)
            cur = conn.cursor()
            epoch_time = time.time()
            cur.execute("INSERT INTO AIRCRAFTSIGHTINGS VALUES(?,?);", (icaohex, epoch_time))
            conn.commit()
            conn.close()
        else:
            p.set_Interesting("False")

        aircraft_session.append(p)
        return True

    mqtt_outline = f"{this_function_name} ==> aircraft info NOT in LOCAL FAADB: {aircraft_id}"
    output_mqtt_no_color("planes/trace", mqtt_outline)
    return False


def db_known_no_hit(aircraft_id):
    this_function_name = sys._getframe().f_code.co_name
    output_mqtt_no_color("planes/trace", this_function_name)
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT * FROM NOHITAIRCRAFT WHERE AIRCRAFTID=?;", (aircraft_id,))
    rows = cur.fetchall()
    cur.close()

    return bool(rows)


def add_if_new_no_hit(aircraft_id):
    this_function_name = sys._getframe().f_code.co_name
    output_mqtt_no_color("planes/trace", this_function_name)
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT * FROM NOHITAIRCRAFT WHERE AIRCRAFTID=?;", (aircraft_id,))
    rows = cur.fetchall()
    cur.close()

    if not rows:
        conn = create_connection(database)
        cur = conn.cursor()
        epoch_time = time.time()
        cur.execute("INSERT INTO NOHITAIRCRAFT VALUES(?,?);", (aircraft_id, epoch_time))
        conn.commit()
        conn.close()
        mqtt_outline = f"{this_function_name} ==> added new known no info aircraft: {aircraft_id}"
        output_mqtt_no_color("planes/trace", mqtt_outline)
        return True
    return False


global aircraft_session, no_hit_session, icao_data, icao_response, icaohex, database, known_plane, str_icao, local_resolve, webservice_calls
global last_cleanup_time_aircraft, purge_minutes_aircraft, known_aircraft, filtered_aircraft, known_no_hit_db, set_outcolor, mqtt_out_color
global alert_count, watchlist_owner, watch_reg, watch_icao, interesting_aircraft_count, exclude_operator_list, exclude_owner_list

# Read environment variables
mqtt_server = os.environ.get('MQTT_SERVER', 'mqtt')
mqtt_user = os.environ.get('MQTT_USER', 'me')
mqtt_pass = os.environ.get('MQTT_PASS', 'me')
database = os.environ.get('DATABASE', '/media/freewill/beed2112/hacktop/fr24db/aircraftMon.db')
receiver_url = os.environ.get('RECEIVER_URL', 'http://adsblistener')



sampling_period = 60
sampling_period_seconds = int(sampling_period)
exclude_operator_list = "LXJ,AAL,ASA,UAL,SWA,FFT,SKW,WJA,FLE,ASH,DAL,ENY,NKS,VOI,JBU,WSW,UPS,SWQ,ABX,FDX,QXE,SLI,EJA,JZA,ROU,GAJ,FDY,CFS,NJAS"
exclude_owner_list = ["Quantum Helicopters Inc", "FedEx"]
watchlist_owner = ["Aces", "ACES", "Missile Defense Agency", "NASCAR", "Motorsports", "Federal", "United States", "Oprah", "Police", "State Farm", "Sherrif", "Arizona Department", "NASA", "Air Force", "Museum", "Google", "Apple", "Penske", "Cardinals", "Stewart-Haas", "Tanker"]
watch_reg = "N44SF,N812LE,N353P,N781MM,N88WR,N383LS,N78HV,N4DP,N9165H,N519JG,N280NV"
watch_icao = "F16,S211,BE18,AJET,KMAX,HGT,ST75,RRR,MRF1,L1P,T6,BGR,TNK,P4Y,A4"


aircraft_session = []
no_hit_session = []

filtered_aircraft = 0
interesting_aircraft_count = 0
alert_count = 0
no_hit = 0
web_service_error = 0
webservice_calls = 0
total_aircraft_count = 0
local_resolve = 0
local_mem_resolve = 0
known_no_hit_db = 0
start_time = time.asctime(time.localtime(time.time()))
last_cleanup_time_aircraft = datetime.today()
purge_minutes_aircraft = 240

this_function_name = "mainLine Startup"
output_mqtt_no_color("planes/trace", this_function_name)
receiver_url = 'http://adsblistener'
adsb_exchange_base = 'https://globe.adsbexchange.com/?icao='

while True:
    this_function_name = f"{sys._getframe().f_code.co_name} forever while loop startup ++++++++++++++++++++++++++++++++++++++++"
    output_mqtt_no_color("planes/trace", this_function_name)

    time_since_last_cleanup_aircraft = datetime.today() - last_cleanup_time_aircraft
    minutes_since_last_cleanup_aircraft = time_since_last_cleanup_aircraft.total_seconds() / 60

    if minutes_since_last_cleanup_aircraft > purge_minutes_aircraft:
        last_cleanup_time_aircraft = datetime.today()
        hold1 = len(aircraft_session)
        clean_aircraft()
        hold2 = len(aircraft_session)
        outline = f"{time.asctime(time.localtime(time.time()))} | Aircraft memory clean up time before {hold1} | after {hold2}"
        print(outline)
        this_function_name = outline
        output_mqtt_no_color("planes/trace", this_function_name)

        hold1 = len(no_hit_session)
        clean_no_hit_aircraft()
        hold2 = len(no_hit_session)
        outline = f"{time.asctime(time.localtime(time.time()))} | noHit memory clean up time before {hold1} | after {hold2}"
        print(outline)
        this_function_name = outline
        output_mqtt_no_color("planes/trace", this_function_name)

    aircraft_count = 0

    try:
        r = requests.get(f'{receiver_url}/dump1090/data/aircraft.json', timeout=(5, 5))
        if r.status_code != 200:
            raise ValueError(f'ERROR: getting aircraft json data :{r.text}')

        aircraft_data = r.json()
        now = aircraft_data['now']
        info_data = {
            'now': now,
            'aircraft_count': len(aircraft_data['aircraft']),
            'messages': aircraft_data['messages']
        }
        this_function_name = " ==> success retrieving aircraft.json"
        output_mqtt_no_color("planes/trace", this_function_name)
        aircraft_count = info_data['aircraft_count']
    except:
        aircraft_count = 0
        this_function_name = " ==> FAILURE retrieving aircraft.json"
        output_mqtt_no_color("planes/trace", this_function_name)

    total_aircraft_count += aircraft_count
    current_time = time.localtime()
    current_hour = current_time.tm_hour
    current_minute = current_time.tm_min
    my_current_time = f"{current_hour}:{current_minute}"

    part1 = "+++"
    part2 = f"-- Strt {my_current_time}--tot seen {total_aircraft_count}-- cur {aircraft_count}-- flt {filtered_aircraft}"
    part4 = f"--wsCall {webservice_calls}--wsErr {web_service_error}"
    part5 = f"--knwnNoHit {known_no_hit_db}--nohit {no_hit}--lclDB {local_resolve}"
    part6 = f"lclMem {local_mem_resolve}--+++"
    outline = f"{part1}{part2}--{part4}--{part5}--{part6}"
    print(outline)

    mqtt_line1 = f"+++--Curr {time.asctime(time.localtime(time.time()))}"
    mqtt_line2 = f"--tot seen {total_aircraft_count}-- cur {aircraft_count}"

    mqtt_out_color = "TFT_ORANGE"
    mqtt_out_line = f"{mqtt_line1}{mqtt_line2}"
    output_mqtt(mqtt_out_color, "planes/console", mqtt_out_line)

    for i in range(aircraft_count):
        icaohex = aircraft_data['aircraft'][i]['hex']
        this_function_name = f"aircraft processing loop STARTS {aircraft_count} aircraft processing #{i+1} ==> {icaohex}"
        output_mqtt_no_color("planes/trace", this_function_name)
        set_outcolor = "white"
        mqtt_out_color = "TFT_WHITE"
        str_icao = ""
        known_no_hit_aircraft = "False"
        known_aircraft = "False"
        if is_known_plane(icaohex):
            known_aircraft = "True"
            local_mem_resolve += 1
            data_source = "memory"
            output_aircraft()
        else:
            if is_known_plane_db(icaohex):
                known_aircraft = "True"
                local_resolve += 1
                data_source = "local"
                output_aircraft()
            else:
                if not db_known_no_hit(icaohex):
                    try:
                        known_no_hit_aircraft = "False"
                        webservice_calls += 1
                        icao_response = requests.get(f'https://hexdb.io/api/v1/aircraft/{icaohex}', timeout=(15, 15))
                        icao_data = icao_response.json()
                        if icao_response.status_code == 200:
                            str_icao = str(icao_data['OperatorFlagCode'])
                            owners = icao_data['RegisteredOwners']
                            str_reg = str(icao_data['Registration'])
                            str_type = str(icao_data['Type'])
                            known_aircraft = "True"
                            data_source = "web"
                            set_outcolor = "cyan"
                            mqtt_out_color = "TFT_CYAN"
                            this_function_name = f"{sys._getframe().f_code.co_name} ==> aircraft info provided be WEBSERVICE {icaohex}"
                            output_mqtt_no_color("planes/trace", this_function_name)
                            add_aircraft(icaohex)
                            output_aircraft()
                        else:
                            add_no_hit(icaohex)
                            no_hit += 1
                            mqtt_outline = f"{icaohex} {no_hit}"
                            output_mqtt_no_color("planes/nohit", mqtt_outline)
                            add_if_new_no_hit(icaohex)
                    except (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, Exception) as e:
                        str_icao = "ERROR"
                        web_service_error += 1
                        print(e)
                        this_function_name = " ==> webservice error"
                        output_mqtt_no_color("planes/trace", this_function_name)
                else:
                    known_no_hit_db += 1
                    this_function_name = " ==> we know we can't find information on this aircraft"
                    output_mqtt_no_color("planes/trace", this_function_name)

        this_function_name = "processing loop ==> "
        output_mqtt_no_color("planes/trace", f"{this_function_name} COMPLETED processing aircraft: {icaohex}")

    this_function_name = f"{sys._getframe().f_code.co_name} aircraft processing loop ENDS"
    output_mqtt_no_color("planes/trace", this_function_name)
    this_function_name = "sleeping..."
    output_mqtt_no_color("planes/trace", this_function_name)
    for _ in range(sampling_period_seconds):
        print(".", end="")
        time.sleep(1)
    print("")

