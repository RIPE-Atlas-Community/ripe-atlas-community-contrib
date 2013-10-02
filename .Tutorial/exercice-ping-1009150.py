#!/usr/bin/env python

# How many probes did not reach the target, even once?
# Which are they? (field prb_id)

# Data is in https://atlas.ripe.net/api/v1/measurement/1009150/result/

import json

file = open("1009150.json")

# Load the data in a JSON obect
results = json.loads(file.read())


# Main loop over the results
for probe in results:
    # Per-test loop
    probe_ok = False
    for test in probe['result']:
        if test.has_key('rtt'):
            probe_ok = True
            break
    if not probe_ok:
        print "Probe %s has a problem" % probe['prb_id']
        
    
