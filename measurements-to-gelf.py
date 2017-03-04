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

# Configuration
gelf_server = 'localhost'
gelf_port = 5555

# Parse Args
if len(sys.argv) == 1:
	print "# Prototype of a RIPE Atlas to GELF parser"
	print "#"
	print "# Usage: python measurements-to-gelf.py <measurement id> <timeframe in min>"
	print "#"
	print "# Example: python measurements-to-gelf.py 12323 5"
	print "#"
	print "# Please define Server and Port inside the script"
	exit(1) 

measurement_id = str(sys.argv[1])
time_window = int(sys.argv[2]) * 60



def getplace(lat, lon):
    url = "http://maps.googleapis.com/maps/api/geocode/json?"
    url += "latlng=%s,%s&sensor=false" % (lat, lon)
    v = urlopen(url).read()
    j = json.loads(v)
    components = j['results'][0]['address_components']
    country = town = None
    for c in components:
        if "country" in c['types']:
            country = c['long_name']
        if "administrative_area_level_1" in c['types']:
            state = c['long_name']
    return state, country


currenttime = int(time.time())
five_ago = currenttime - time_window

measurement_url = "https://atlas.ripe.net/api/v2/measurements/" + measurement_id + "/results?start=" + str(five_ago)  +"&stop=" + str(currenttime)  + "&format=json"

print measurement_url

try:
	d = requests.get(measurement_url)
except Exception as e:
        print e
	exit(1)

data = d.json()

gelf = UdpClient(gelf_server, port=gelf_port)
for probe in data:
	print probe['prb_id']
	log = {}
	v = requests.get('https://atlas.ripe.net/api/v1/probe/' + str(probe['prb_id']) + '/')
	details = v.json()
	location = getplace(details['latitude'], details['longitude'])
	log['short_message'] = 'RIPE Atlas Data of Probe ' + str(probe['prb_id'])
	log['host'] = 'ripe-atlas'
	log['level'] = syslog.LOG_INFO
	log['_ripe_atlas_prbid'] = probe['prb_id']
	log['_ripe_atlas_dst_addr'] = probe['dst_addr']
	log['_ripe_atlas_src_addr'] = probe['from']
	log['_ripe_atlas_type'] = probe['type']
	log['_ripe_atlas_proto'] = probe['proto']
	log['_ripe_atlas_sent_pkts'] = probe['sent']
	log['_ripe_atlas_country'] = details['country_code']
	log['_ripe_atlas_location'] = location[0] + ',' + location[1]
	log['_ripe_atlas_rcvd_pkts'] = probe['rcvd']
	log['_ripe_atlas_timestamp'] = probe['timestamp']
	log['_ripe_atlas_avg_rtt'] = probe['avg']
	log['_ripe_atlas_max_rtt'] = probe['max']
	log['_ripe_atlas_min_rtt'] = probe['min']
	gelf.log(log)



