#!/usr/bin/env python

# Data is in https://atlas.ripe.net/api/v1/measurement/1009150/result/

import json

file = open("1009150.json")

# Load the data in a JSON obect
results = json.loads(file.read())

# Initialize
timeouts = 0
errors = 0
num_rtt = 0
total_rtt = 0

# Main loop over the results
for probe in results:
    
    # Per-test loop
    for test in probe['result']:
        if test.has_key('x'):
            timeouts += 1
        elif test.has_key('error'):
            errors += 1
        elif test.has_key('rtt'):
            num_rtt += 1
            total_rtt += test['rtt']

print "%i results, %i timeouts, %i errors, average RTT %.2f ms" % \
      (len(results), timeouts, errors, total_rtt/num_rtt)
