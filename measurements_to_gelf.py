#!/usr/bin/python

#
# Prototype of a RIPE Atlas to GELF parser by awlx 
#
# Usage: python measurements-to-gelf.py <id> <min>
#

# Imports
from gelfclient import UdpClient
from urllib2 import urlopen
import syslog
import json
import time
import sys
import requests
import sqlite3
from os.path import isfile, getsize
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


# Configuration
gelf_server = 'localhost'
gelf_port = 5555
api_key = '<api_key>'
db_file = 'geocache.db'

# Parse Args
if len(sys.argv) == 1:
    print("# Prototype of a RIPE Atlas to GELF parser")
    print("#")
    print("# Usage: python measurements-to-gelf.py <measurement id> <timeframe in min>")
    print("#")
    print("# Example: python measurements-to-gelf.py 12323 5")
    print("#")
    print("# Please define Server and Port inside the script.")
    print("# Get an API Key for Geolocation from https://geocoder.opencagedata.com/pricing")
    exit(1) 

measurement_id = str(sys.argv[1])
time_frame_secs = int(sys.argv[2]) * 60

current_time = int(time.time())
time_frame = current_time - time_frame_secs

def do_db_check():
    if not isfile(db_file):
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()
        sql_command = """
        CREATE TABLE geocache ( 
        id INTEGER PRIMARY KEY, 
        expiry INTEGER,
        lat FLOAT, 
        lon FLOAT, 
        country VARCHAR(30), 
        state VARCHAR(30));"""
        cursor.execute(sql_command)
    else:
        connection = sqlite3.connect(db_file)
    return connection

def do_db_insert(connection, expiry, lat, lon, country, state):
    cursor = connection.cursor()
    format_str = """INSERT INTO geocache (id, expiry, lat, lon, country, state)
    VALUES (NULL, {expiry}, {lat}, {lon}, "{country}", "{state}");"""
    sql_command = format_str.format(expiry=expiry, lat=lat, lon=lon, country = country, state=state) 
    cursor.execute(sql_command)
    connection.commit()

def do_db_select(cursor, lat, lon):
    format_str = """SELECT expiry,country,state FROM geocache WHERE lat="{lat}" AND lon="{lon}";"""
    sql_command = format_str.format(lat=lat, lon=lon)
    cursor.execute(sql_command)
    location = cursor.fetchone()
    return location
    
def do_db_delete(connection, expiry):
    cursor = connection.cursor()
    format_str = """DELETE FROM geocache WHERE expiry = "{expiry}";"""
    sql_command = format_str.format(expiry=expiry)
    cursor.execute(sql_command)
    connection.commit()

# Get things done
def get_place(lat, lon, current_time):
    url = "http://api.opencagedata.com/geocode/v1/json?q="
    url += "%s+%s&key=%s" % (lat, lon, api_key)
    connection = do_db_check()
    cursor = connection.cursor()
    location = do_db_select(cursor, lat, lon)
    expiry = current_time + 30;
    if location is None:
        try:    
            content_geo_raw = urlopen(url).read()
            content_geo_json = json.loads(content_geo_raw)
            components = content_geo_json['results'][0]['components']
            country = town = None
            country = components['country']
            state = components['state']
        except Exception as e:
            country = "N/A"
            state = "N/A"
        do_db_insert(connection, expiry, lat, lon, country, state)
    else:
        expiry = location[0]
        state = location[1]
        country = location[2]
        if expiry <= current_time:
            do_db_delete(connection, expiry)
    return state, country

measurement_url = "https://atlas.ripe.net/api/v2/measurements/{}/results?{}".format(
    measurement_id,
    urlencode({
        "start": time_frame,
        "stop": current_time,
        "format": "json"
    })
)

print(measurement_url)

try:
    d = requests.get(measurement_url)
except Exception as e:
    print e
    exit(1)

data = d.json()

gelf = UdpClient(gelf_server, port=gelf_port)
for probe in data:
    print(probe['prb_id'])
    log = {}
    content_probes_raw = requests.get('https://atlas.ripe.net/api/v1/probe/' + str(probe['prb_id']) + '/')
    details = content_probes_raw.json()
    location = get_place(details['latitude'], details['longitude'], current_time)
    log['short_message'] = 'RIPE Atlas Data of Probe ' + str(probe['prb_id'])
    log['host'] = 'ripe-atlas'
    log['level'] = syslog.LOG_INFO
    log['timestamp'] = probe['timestamp']
    log['_ripe_atlas_prbid'] = probe['prb_id']
    log['_ripe_atlas_dst_addr'] = probe['dst_addr']
    log['_ripe_atlas_src_addr'] = probe['from']
    log['_ripe_atlas_type'] = probe['type']
    log['_ripe_atlas_proto'] = probe['proto']
    log['_ripe_atlas_sent_pkts'] = probe['sent']
    log['_ripe_atlas_country'] = details['country_code']
    log['_ripe_atlas_location'] = location[0] + ',' + location[1]
    log['_ripe_atlas_rcvd_pkts'] = probe['rcvd']
    log['_ripe_atlas_avg_rtt'] = probe['avg']
    log['_ripe_atlas_max_rtt'] = probe['max']
    log['_ripe_atlas_min_rtt'] = probe['min']
    gelf.log(log)

