#!/usr/bin/env python

import RIPEAtlas

data = {'definitions': [
    {'target': '192.0.2.1', 'af': 4, 'packets': 3, 
     'type': 'ping', 'is_oneoff': True, 
     'description': 'Ping 192.0.2.1 from GR'}], 
      'probes': [
            {'requested': 5, 'type': 'country', 
             'value': 'GR'}]}

# If the key is in ~/.atlas/auth
measurement = RIPEAtlas.Measurement(data)
print "Measurement %s started" % measurement.id
rdata = measurement.results(wait=True, percentage_required=0.99)
print "Finished. %d probes reported" % len(rdata)

