#!/usr/bin/env python

import json
import urllib2

key = "XXX"
url = "https://atlas.ripe.net/api/v1/measurement/?key=%s" % key
data = {'definitions': [
    {'target': '192.0.2.1', 'af': 4, 'packets': 3, 
     'type': 'ping', 'is_oneoff': True, 
     'description': 'Ping 192.0.2.1 from GR'}], 
      'probes': [
            {'requested': 5, 'type': 'country', 
             'value': 'GR'}]}

request = urllib2.Request(url)
request.add_header("Content-Type", "application/json")
request.add_header("Accept", "application/json")
json_data = json.dumps(data)
conn = urllib2.urlopen(request, json_data)

results = json.load(conn)
print("Measurement #%s started" % (results["measurements"]))
