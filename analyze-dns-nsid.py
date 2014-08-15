#!/usr/bin/env python

""" Python code to analyze RIPE Atlas UDM (User-Defined Measurements)
results. This one is for DNS NSID queries (find the identity of a name
server). It uses a RIPE Atlas JSON file as input or a reference to a
public measurement.

Stephane Bortzmeyer <bortzmeyer@nic.fr>
"""

import json
import sys
import base64
import collections
import urllib
import getopt

# DNS Python http://www.dnspython.org/
import dns.message

class Items:
    def __init__(self):
        self.num = 0

def by_num(l, r):
    return -cmp(ns_names[l].num, ns_names[r].num)

def usage(msg=None):
    print >>sys.stderr, "Usage: %s [-f file] [-d measurement]" % sys.argv[0]
    if msg is not None:
        print >>sys.stderr, msg

# Try measurement #1008591 for instance

results = None
try:
    optlist, args = getopt.getopt (sys.argv[1:], "f:d:", ["file=","data-api="])
    for option, value in optlist:
        if option == "--file" or option == "-f":
            results = json.loads(open(value).read())
        elif option == "--data-api" or option == "-d":
            url = "https://atlas.ripe.net/api/v1/measurement/" + value + "/result/"
            results = json.load(urllib.urlopen(url))
        else:
            usage("Unknown option %s" % option)
            sys.exit(1)

except getopt.error, reason:
    usage(reason)
    sys.exit(1)
if results is None:
    if len(args) == 1:
        results = json.loads(open(args[0]).read())
    else:
        usage("One of -f or -d is mandatory")
        sys.exit(1)
net_failures = 0
nsid_failures = 0
successes = 0
probes = collections.defaultdict(Items)
ns_names = collections.defaultdict(Items)
for result in results:
    probes[result['prb_id']].num += 1
    if not result.has_key('result'):
       net_failures += 1
    else:
        answer = result['result']['abuf'] + "=="
        content = base64.b64decode(answer)
        msg = dns.message.from_wire(content)
        ns_name = None
        for opt in msg.options:
            if opt.otype == dns.edns.NSID:
                ns_name = opt.data
                ns_names[ns_name].num += 1
        if ns_name is not None:
            successes += 1
        else:
            nsid_failures += 1
if len(results) != len(probes):
    print >>sys.stderr, "%i results but %i probes" % (len(results), len(probes))
    sys.exit(1)
print "%i probes, %i successes, %i network failures, %i NSID failures" % (len(probes),
                                                                          successes, net_failures, nsid_failures)
names = ns_names.keys()
names.sort(by_num)
for ns in names:
    print "%s: %i (%.0f %%)" % (ns, ns_names[ns].num, ns_names[ns].num*100.0/successes)
