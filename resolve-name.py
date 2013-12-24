#!/usr/bin/python

""" Python code to start a RIPE Atlas UDM (User-Defined
Measurement). This one is for running DNS to resolve a name from many
places, in order to survey local cache poisonings, effect of
hijackings and other DNS rejuvenation effects.

You'll need an API key in ~/.atlas/auth.

After launching the measurement, it downloads the results and analyzes
them.

Stephane Bortzmeyer <bortzmeyer@nic.fr>
"""

import json
import sys
import time
import base64
import getopt
import collections

# DNS Python http://www.dnspython.org/
import dns.message

import RIPEAtlas

requested = 500
qtype = 'A'
measurement_id = None
sort = False

class Set():
    def __init__(self):
        self.total = 0

def usage(msg=None):
    if msg:
        print >>sys.stderr, msg
    print >>sys.stderr, "Usage: %s domain-name" % sys.argv[0]
    print >>sys.stderr, """Options are:
    --help or -h : this message
    --type or -t : query type (default is %s)
    --requested=N or -r N : requests N probes (default is %s)
    --measurement-ID=N or -m N : do not start a measurement, just analyze a former one
    """ % (qtype, requested)

try:
    optlist, args = getopt.getopt (sys.argv[1:], "r:t:hm:s",
                               ["requested=", "type=", "sort", "help"])
    for option, value in optlist:
        if option == "--type" or option == "-t":
            qtype = value
        elif option == "--requested" or option == "-r":
            requested = int(value)
        elif option == "--sort" or option == "-s":
            sort = True
        elif option == "--measurement-ID" or option == "-m":
            measurement_id = value
        elif option == "--help" or option == "-h":
            usage()
            sys.exit(0)
        else:
            # Should never occur, it is trapped by getopt
            usage("Unknown option %s" % option)
            sys.exit(1)
except getopt.error, reason:
    usage(reason)
    sys.exit(1)

if len(args) != 1:
    usage()
    sys.exit(1)

domainname = args[0]

if measurement_id is None:
    data = { "definitions": [{ "type": "dns", "af": 4, "is_oneoff": True, 
                           "use_probe_resolver": True, "query_argument": domainname,
                           "description": "DNS resolution of %s" % domainname,
                           "query_class": "IN", "query_type": qtype, 
                           "recursion_desired": True}],
         "probes": [{"requested": requested, "type": "area", "value": "WW"}] }
    
    measurement = RIPEAtlas.Measurement(data,
                                    lambda delay: sys.stderr.write(
        "Sleeping %i seconds...\n" % delay))

    print "Measurement #%s for %s/%s uses %i probes" % \
      (measurement.id, domainname, qtype, measurement.num_probes)

    measurement_id = measurement.id
    results = measurement.results(wait=True)
else:
    measurement = RIPEAtlas.Measurement(data=None, id=measurement_id)
    results = measurement.results(wait=False)
    
probes = 0
successes = 0

qtype_num = dns.rdatatype.from_text(qtype) # Raises dns.rdatatype.UnknownRdatatype if unknown
sets = collections.defaultdict(Set)
for result in results:
    probes += 1
    if result.has_key("result"):
        try:
            answer = result['result']['abuf'] + "=="
            content = base64.b64decode(answer)
            msg = dns.message.from_wire(content)
            successes += 1
            myset = []
            for rrset in msg.answer:
                for rdata in rrset:
                    if rdata.rdtype == qtype_num:
                        myset.append(str(rdata))
            myset.sort()
            set_str = " ".join(myset)
            sets[set_str].total += 1
        except dns.message.TrailingJunk:
            print "Probe %s failed (trailing junk)" % result['prb_id']
if sort:
    sets_data = sorted(sets, key=lambda s: sets[s].total, reverse=True)
else:
    sets_data = sets
for myset in sets_data:
    print "[%s] : %i occurrences" % (myset, sets[myset].total)

print ("Test done at %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
print ""
