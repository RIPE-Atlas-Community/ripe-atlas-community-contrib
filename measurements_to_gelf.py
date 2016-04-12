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
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


# Configuration
gelf_server = 'localhost'
gelf_port = 5555
api_key = '<api_key>'

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


# Get things done
def get_place(lat, lon):
    url = "http://api.opencagedata.com/geocode/v1/json?q="
    url += "%s+%s&key=%s" % (lat, lon, api_key)
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
    location = get_place(details['latitude'], details['longitude'])
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

