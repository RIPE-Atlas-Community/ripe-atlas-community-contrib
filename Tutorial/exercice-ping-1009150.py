#!/usr/bin/env python

# How many probes did not reach the target, even once?
# Which are they? (field prb_id)

# Data is in https://atlas.ripe.net/api/v1/measurement/1009150/result/

import json

file = open("1009150.json")

# Load the data in a JSON obect
results = json.loads(file.read())


# Main loop over the results
unreachable = set()
for probe in results:
    # Per-test loop
    probe_ok = False
    for test in probe['result']:
        if test.has_key('rtt'):
            probe_ok = True
            break
    if not probe_ok:
        unreachable.add(probe['prb_id'])
if len(unreachable) == 0:
    print "All probes were reachable"
elif len(unreachable) == 1:
    print "One probe was unreachable"
else:
    print "%d probes were unreachable" % len(unreachable)
for prb_id in unreachable:
    print "Probe %s has a problem" % prb_id
