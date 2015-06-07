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
import string
import base64
import getopt
import collections

# DNS Python http://www.dnspython.org/
import dns.message

import RIPEAtlas

# Default values
country = None # World-wide
asn = None # All
prefix = None # All
area = None # World-wide
requested = 500
qtype = 'A'
measurement_id = None
nameserver = None
sort = False
only_one_per_probe = True
ip_family = 4
verbose = False

class Set():
    def __init__(self):
        self.total = 0

def usage(msg=None):
    if msg:
        print >>sys.stderr, msg
    print >>sys.stderr, "Usage: %s domain-name" % sys.argv[0]
    print >>sys.stderr, """Options are:
    --help or -h : this message
    --verbose or -v : more talkative
    --type or -t : query type (default is %s)
    --ipv6 or -6 : contact only the IPv6 probes (do not affect the selection of the DNS resolvers)
    --severalperprobe or -p : count all the resolvers of each probe (default is to count only the first to reply)
    --requested=N or -r N : requests N probes (default is %s)
    --country=2LETTERSCODE or -c 2LETTERSCODE : limits the measurements to one country (default is world-wide)
    --area=AREACODE or -a AREACODE : limits the measurements to one area such as North-Central (default is world-wide)
    --prefix=PREFIX or -f PREFIX : limits the measurements to one IP prefix (default is all prefixes)
    --asn=ASnumber or -n ASnumber : limits the measurements to one AS (default is all ASes)
    --measurement-ID=N or -m N : do not start a measurement, just analyze a former one
    --nameserver=IPaddr or -e IPaddr : query this name server (default is to query the probe's resolver)
    """ % (qtype, requested)

try:
    optlist, args = getopt.getopt (sys.argv[1:], "r:c:a:n:t:e:hm:sp6f:v",
                               ["requested=", "type=", "country=", "area=", "asn=", "prefix=", "nameserver=",
                                "sort", "help", "severalperprobe", "ipv6", "verbose"])
    for option, value in optlist:
        if option == "--type" or option == "-t":
            qtype = value
        elif option == "--country" or option == "-c":
            country = value
        elif option == "--area" or option == "-a":
            area = value
        elif option == "--asn" or option == "-n":
            asn = value
        elif option == "--prefix" or option == "-f":
            prefix = value
        elif option == "--requested" or option == "-r":
            requested = int(value)
        elif option == "--sort" or option == "-s":
            sort = True
        elif option == "--measurement-ID" or option == "-m":
            measurement_id = value
        elif option == "--nameserver" or option == "-e":
            nameserver = value
        elif option == "--help" or option == "-h":
            usage()
            sys.exit(0)
        elif option == "--severalperprobe" or option == "-p":
            only_one_per_probe = False
        elif option == "--ipv6" or option == "-6":
            ip_family = 6
        elif option == "--verbose" or option == "-v":
            verbose = True
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
    data = { "definitions": [{ "type": "dns", "af": ip_family, "is_oneoff": True, 
                           "query_argument": domainname,
                           "description": "DNS resolution of %s" % domainname,
                           "query_class": "IN", "query_type": qtype, 
                           "recursion_desired": True}],
         "probes": [{"requested": requested, "type": "area", "value": "WW"}] }
    if country is not None:
        if asn is not None or area is not None or prefix is not None:
            usage("Specify country *or* area *or* ASn *or* prefix")
            sys.exit(1)
        data["probes"][0]["type"] = "country"
        data["probes"][0]["value"] = country
        data["definitions"][0]["description"] += (" from %s" % country)
    elif area is not None:
        if asn is not None or country is not None or prefix is not None:
            usage("Specify country *or* area *or* ASn *or* prefix")
            sys.exit(1)
        data["probes"][0]["type"] = "area"
        data["probes"][0]["value"] = area
        data["definitions"][0]["description"] += (" from %s" % area)
    elif asn is not None:
        if area is not None or country is not None or prefix is not None:
            usage("Specify country *or* area *or* ASn *or* prefix")
            sys.exit(1)
        data["probes"][0]["type"] = "asn"
        data["probes"][0]["value"] = asn
        data["definitions"][0]["description"] += (" from AS #%s" % asn)
    elif prefix is not None:
        if area is not None or country is not None or asn is not None:
            usage("Specify country *or* area *or* ASn *or* prefix")
            sys.exit(1)
        data["probes"][0]["type"] = "prefix"
        data["probes"][0]["value"] = prefix
        data["definitions"][0]["description"] += (" from prefix %s" % prefix)
    else:
        data["probes"][0]["type"] = "area"
        data["probes"][0]["value"] = "WW"
    if nameserver is None:
        data["definitions"][0]["use_probe_resolver"] = True
    else:
        data["definitions"][0]["use_probe_resolver"] = False
        data["definitions"][0]["target"] = nameserver
        
    if verbose:
        print data
        
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
    if result.has_key("resultset"):
        for result_i in result['resultset']:
            if result_i.has_key("result"):
                try:
                    answer = result_i['result']['abuf'] + "=="
                    content = base64.b64decode(answer)
                    msg = dns.message.from_wire(content)
                    successes += 1
                    myset = []
                    for rrset in msg.answer:
                        for rdata in rrset:
                            if rdata.rdtype == qtype_num:
                                myset.append(string.lower(str(rdata)))
                    myset.sort()
                    set_str = " ".join(myset)
                    sets[set_str].total += 1
                except dns.message.TrailingJunk:
                    print "Probe %s failed (trailing junk)" % result['prb_id']
            if only_one_per_probe:
                break
    elif result.has_key("result"):
            # TODO: timeouts (and may be other errors) return the same
            # empty set, we should analyze more deeply.
            try:
                answer = result['result']['abuf'] + "=="
                content = base64.b64decode(answer)
                msg = dns.message.from_wire(content)
                successes += 1
                myset = []
                for rrset in msg.answer:
                    for rdata in rrset:
                        if rdata.rdtype == qtype_num:
                            myset.append(string.lower(str(rdata)))
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
