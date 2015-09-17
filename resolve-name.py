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
# TODO: bits DO and CD, UDP payload size https://atlas.ripe.net/docs/measurement-creation-api/
country = None # World-wide
asn = None # All
prefix = None # All
area = None # World-wide
old_measurement = None
probe_to_use = None
requested = 500
qtype = 'A'
measurement_id = None
display_probes = False
display_resolvers = False
machine_readable = False
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
    --machinereadable or -b : machine-readable output, to be consumed by tools like grep or cut
    --displayprobes or -o : display the probes numbers (WARNING: big lists)
    --displayresolvers or -l : display the resolvers IP addresses (WARNING: big lists)
    --sort or -s : sort the result sets
    --type or -t : query type (default is %s)
    --ipv6 or -6 : contact only the IPv6 probes (do not affect the selection of the DNS resolvers)
    --severalperprobe or -p : count all the resolvers of each probe (default is to count only the first to reply)
    --requested=N or -r N : requests N probes (default is %s)
    --country=2LETTERSCODE or -c 2LETTERSCODE : limits the measurements to one country (default is world-wide)
    --area=AREACODE or -a AREACODE : limits the measurements to one area such as North-Central (default is world-wide)
    --prefix=PREFIX or -f PREFIX : limits the measurements to one IP prefix (default is all prefixes)
    --asn=ASnumber or -n ASnumber : limits the measurements to one AS (default is all ASes)
    --probetouse or -u N : uses only this probe
    --old_measurement MSMID or -g MSMID : uses the probes of measurement #MSMID
    --measurement-ID=N or -m N : do not start a measurement, just analyze a former one
    --nameserver=IPaddr[,...] or -e IPaddr : query this name server (default is to query the probe's resolver)
    """ % (qtype, requested)
    
try:
    optlist, args = getopt.getopt (sys.argv[1:], "r:c:a:n:t:oe:hm:g:sp6u:f:vbl",
                               ["requested=", "type=", "old_measurement=", "displayprobes", "displayresolvers", "probetouse=", "country=", "area=", "asn=", "prefix=", "nameserver=",
                                "sort", "help", "severalperprobe", "ipv6", "verbose", "machine_readable"])
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
        elif option == "--old_measurement" or option == "-g":
            old_measurement = value
        elif option == "--measurement-ID" or option == "-m":
            measurement_id = value
        elif option == "--probetouse" or option == "-u":
            probe_to_use = value
        elif option == "--nameserver" or option == "-e":
            nameserver = value
            nameservers = string.split(nameserver, ",")
        elif option == "--help" or option == "-h":
            usage()
            sys.exit(0)
        elif option == "--displayprobes" or option == "-o":
            display_probes = True
        elif option == "--displayresolvers" or option == "-l":
            display_resolvers = True
        elif option == "--severalperprobe" or option == "-p":
            only_one_per_probe = False
        elif option == "--ipv6" or option == "-6":
            ip_family = 6
            # TODO: when using option --nameserver, set it automatically depending on the address family?
        elif option == "--verbose" or option == "-v":
            verbose = True
        elif option == "--machinereadable" or option == "-b":
            machine_readable = True
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
    if probe_to_use is not None:
        requested = 1 # TODO allow several -u options
    data = { "definitions": [{ "type": "dns", "af": ip_family, "is_oneoff": True, 
                           "query_argument": domainname,
                           "description": "DNS resolution of %s" % domainname,
                           "query_class": "IN", "query_type": qtype, 
                           "recursion_desired": True}],
         "probes": [{"requested": requested, "type": "area", "value": "WW"}] }
    if probe_to_use is not None:
        # TODO: should warn if --requested was specified
        if country is not None or area is not None or asn is not None or prefix is not None:
            usage("Specify a given probe *or* (country or area or ASn or prefix)")
            sys.exit(1)
        data["probes"][0]["type"] = "probes"
        data["probes"][0]["value"] = str(probe_to_use)
    else:
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
        elif old_measurement is not None:
            if area is not None or country is not None or asn is not None:
                usage("Specify country *or* area *or* ASn *or* old measurement")
                sys.exit(1)
        else:
            data["probes"][0]["type"] = "area"
            data["probes"][0]["value"] = "WW"
    if verbose and machine_readable:
        usage("Specify verbose *or* machine-readable output")
        sys.exit(1)
    if (display_probes or display_resolvers) and machine_readable:
        usage("Display probes/resolvers *or* machine-readable output")
        sys.exit(1)

    if nameserver is None:
        nameservers = [None,]
        
    for nameserver in nameservers:
        if nameserver is None:
            data["definitions"][0]["use_probe_resolver"] = True
        else:
            data["definitions"][0]["use_probe_resolver"] = False
            data["definitions"][0]["target"] = nameserver
            data["definitions"][0]["description"] += (" via nameserver %s" % nameserver)

        if old_measurement is not None:
            data["probes"][0]["requested"] = 500 # Dummy value, anyway,
                                                    # but necessary to get
                                                    # all the probes
            # TODO: the huge value of "requested" makes us wait a very long time
            data["probes"][0]["type"] = "msm"
            data["probes"][0]["value"] = old_measurement
            data["definitions"][0]["description"] += (" from probes of measurement #%s" % old_measurement)

        if measurement_id is None:
            if verbose:
                print data
            measurement = RIPEAtlas.Measurement(data,
                                            lambda delay: sys.stderr.write(
                    "Sleeping %i seconds...\n" % delay))

            if not machine_readable:
                print "Measurement #%s for %s/%s uses %i probes" % \
                (measurement.id, domainname, qtype, measurement.num_probes)

            old_measurement = measurement.id
            results = measurement.results(wait=True)
        else:
            measurement = RIPEAtlas.Measurement(data=None, id=measurement_id)
            results = measurement.results(wait=False)

        probes = 0
        successes = 0

        qtype_num = dns.rdatatype.from_text(qtype) # Raises dns.rdatatype.UnknownRdatatype if unknown
        sets = collections.defaultdict(Set)
        if display_probes:
            probes_sets = collections.defaultdict(Set)
        if display_resolvers:
            resolvers_sets = collections.defaultdict(Set)
        for result in results:
            probes += 1
            probe_id = result["prb_id"]
            if result.has_key("resultset"):
                for result_i in result['resultset']:
                    if result_i.has_key("result"):
                        try:
                            resolver = str(result_i['dst_addr'])
                            answer = result_i['result']['abuf'] + "=="
                            content = base64.b64decode(answer)
                            msg = dns.message.from_wire(content)
                            successes += 1
                            myset = []
                            if msg.rcode() == dns.rcode.NOERROR:
                                for rrset in msg.answer:
                                    for rdata in rrset:
                                        if rdata.rdtype == qtype_num:
                                            myset.append(string.lower(str(rdata)))
                            else:
                                myset.append("ERROR: %s" % dns.rcode.to_text(msg.rcode()))
                            myset.sort()
                            set_str = " ".join(myset)
                            sets[set_str].total += 1
                            if display_probes:
                                if probes_sets.has_key(set_str):
                                    probes_sets[set_str].append(probe_id)
                                else:
                                    probes_sets[set_str] = [probe_id,]
                            if display_resolvers:
                                if resolvers_sets.has_key(set_str):
                                    if not (resolver in resolvers_sets[set_str]):
                                        resolvers_sets[set_str].append(resolver)
                                else:
                                    resolvers_sets[set_str] = [resolver,]
                        except dns.message.TrailingJunk:
                            if not machine_readable:
                                print "Probe %s failed (trailing junk)" % result['prb_id']
                    if only_one_per_probe:
                        break
            elif result.has_key("result"):
                    try:
                        resolver = str(result['dst_addr'])
                        answer = result['result']['abuf'] + "=="
                        content = base64.b64decode(answer)
                        msg = dns.message.from_wire(content)
                        successes += 1
                        myset = []
                        if msg.rcode() == dns.rcode.NOERROR:
                            for rrset in msg.answer:
                                for rdata in rrset:
                                    if rdata.rdtype == qtype_num:
                                        myset.append(string.lower(str(rdata)))
                        else:
                            myset.append("ERROR: %s" % dns.rcode.to_text(msg.rcode()))
                        myset.sort()
                        set_str = " ".join(myset)
                        sets[set_str].total += 1
                        if display_probes:
                                if probes_sets.has_key(set_str):
                                    probes_sets[set_str].append(probe_id)
                                else:
                                    probes_sets[set_str] = [probe_id,]
                        if display_resolvers:
                                if resolvers_sets.has_key(set_str):
                                    if not (resolver in resolvers_sets[set_str]):
                                        resolvers_sets[set_str].append(resolver)
                                else:
                                    resolvers_sets[set_str] = [resolver,]
                    except dns.message.TrailingJunk:
                        if not machine_readable:
                            print "Probe %s failed (trailing junk)" % result['prb_id']
        if sort:
            sets_data = sorted(sets, key=lambda s: sets[s].total, reverse=True)
        else:
            sets_data = sets
        details = []
        if not machine_readable and nameserver is not None:
                print "Nameserver %s" % nameserver
        for myset in sets_data:
            detail = ""
            if display_probes:
                detail = "(probes %s)" % probes_sets[myset]
            if display_resolvers:
                detail += "(resolvers %s)" % resolvers_sets[myset]
            if not machine_readable:
                print "[%s] : %i occurrences %s" % (myset, sets[myset].total, detail)
            else:
                details.append("[%s];%i" % (myset, sets[myset].total))

        if not machine_readable:
            print ("Test done at %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            print ""
        else:
            if nameserver is None:
                ns = "DEFAULT RESOLVER"
            else:
                ns = nameserver
            print ",".join([domainname, qtype, str(measurement.id), "%s/%s" % (len(results), measurement.num_probes), \
                            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), ns] + details)
