#!/usr/bin/env python

import json
import sys
import time

# Measurement #1025096 for instance
filename = sys.argv[1]

results = json.loads(open(filename).read())

tests = 0
timeouts = 0
errors = 0
rts = 0
starttimes = []
rtpertime = []
for i in range(0,24):
    starttimes.append(0)
    rtpertime.append(0)
for result in results:
    tests += 1
    if result.has_key('error'):
        if result['error'].has_key('timeout'):
            timeouts += 1
        else:
            errors += 1
    elif result.has_key('result'):
        if result['result'].has_key('rt'):
            rts += 1
            starttime = time.gmtime(result['timestamp'])
            starttimes[starttime.tm_hour] += 1
            rtpertime[starttime.tm_hour] += float(result['result']['rt'])
        else:
             raise Exception("Probe %s has no rt in the result" % result['prb_id'])
    else:
        raise Exception("Probe %s has no result nor error" % result['prb_id'])
for i in range(0,24):
    print "%i %.2f" %(i, rtpertime[i]/starttimes[i])
