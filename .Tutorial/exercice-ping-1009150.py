#!/usr/bin/env python

# How many probes did not reach the target, even once?
# Which are they? (field prb_id)

# Data is in https://atlas.ripe.net/api/v1/measurement/1009150/result/

import json

file = open("1009150.json")

# Load the data in a JSON obect
results = json.loads(file.read())


# Main loop over the results
unreachable = 0
for probe in results:
    # Per-test loop
    probe_ok = False
    for test in probe['result']:
        if test.has_key('rtt'):
            probe_ok = True
            break
    if not probe_ok:
        unreachable += 1
        print "Probe %s has a problem" % probe['prb_id']
if unreachable == 0:
    print "All probes were reachable"
elif unreachable == 1:
    print "One probe was unreachable"
elif unreachable > 1:
    print "%d probes were unreachable" % unreachable
