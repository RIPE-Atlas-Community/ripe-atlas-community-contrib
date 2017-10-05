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
old_measurement = None
probe_to_use = None
requested = 5
qtype = 'A'
measurement_id = None
display_probes = False
display_resolvers = False
display_rtt = False
display_validation = False
edns_size = None
dnssec = False
dnssec_checking = True
machine_readable = False
nameserver = None
recursive = True
sort = False
nsid = False
only_one_per_probe = True
ip_family = 4
verbose = False
protocol = "UDP"

# Constants
MAXLEN = 80 # Maximum length of a displayed resource record

class Set():
    def __init__(self):
        self.total = 0
        self.rtt = 0

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
    --norecursive or -z : asks the resolver to NOT recurse (default is to recurse, note --norecursive works ONLY if asking a specific resolver, not with the default one)
    --dnssec or -d : asks the resolver the DNSSEC records
    --nsid : asks the resolver with NSID (name server identification)
    --ednssize=N or -q N : asks for EDNS with the "payload size" option (default is very old DNS, without EDNS)
    --tcp: uses TCP (default is UDP)
    --checkingdisabled or -k : asks the resolver to NOT perform DNSSEC validation
    --displayvalidation or -j : displays the DNSSEC validation status
    --displayrtt or -i : displays the average RTT
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
    --measurement_ID=N or -m N : do not start a measurement, just analyze a former one (do *not* forget to use the same -t)
    --nameserver=IPaddr[,...] or -e IPaddr : query this name server (default is to query the probe's resolver)
    """ % (qtype, requested)
    
try:
    optlist, args = getopt.getopt (sys.argv[1:], "a:bc:de:f:g:hijklm:n:opq:r:st:u:v6z",
                               ["requested=", "type=", "old_measurement=", "measurement_ID=", "ednssize=",
                                "displayprobes", "displayresolvers",
                                "displayrtt", "displayvalidation", "dnssec", "nsid", "norecursive", "tcp", "checkingdisabled",
                                "probetouse=", "country=", "area=", "asn=", "prefix=", "nameserver=",
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
        elif option == "--norecursive" or option == "-z":
            recursive = False
        elif option == "--dnssec" or option == "-d":
            dnssec = True
        elif option == "--nsid":
            nsid = True
        elif option == "--ednssize" or option == "-q":
            edns_size = int(value)
        elif option == "--tcp":
            protocol = "TCP"
        elif option == "--checkingdisabled" or option == "-k":
            dnssec_checking = False
        elif option == "--sort" or option == "-s":
            sort = True
        elif option == "--old_measurement" or option == "-g":
            old_measurement = value
        elif option == "--measurement_ID" or option == "-m":
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
        elif option == "--displayvalidation" or option == "-j":
            display_validation = True
        elif option == "--displayrtt" or option == "-i":
            display_rtt = True
        elif option == "--severalperprobe" or option == "-p":
            only_one_per_probe = False
        elif option == "--ipv6" or option == "-6":
            ip_family = 6
            # TODO: when using option --nameserver, set it
            # automatically depending on the address family? Not easy,
            # the nameserver can be identified by name. Forbid it?
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
data = { "is_oneoff": True,
         "definitions": [{ "type": "dns", "af": ip_family, 
                       "query_argument": domainname,
                       "description": "DNS resolution of %s" % domainname,
                       "query_class": "IN", "query_type": qtype}],
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
if edns_size is not None and protocol == "UDP":
    data["definitions"][0]["udp_payload_size"] = edns_size
if dnssec or display_validation: # https://atlas.ripe.net/docs/api/v2/reference/#!/measurements/Dns_Type_Measurement_List_POST
    data["definitions"][0]["set_do_bit"] = True
    if edns_size is None and protocol == "UDP":
        data["definitions"][0]["udp_payload_size"] = 4096
if nsid: 
    data["definitions"][0]["set_nsid_bit"] = True
    if edns_size is None and protocol == "UDP":
        data["definitions"][0]["udp_payload_size"] = 1024
if not dnssec_checking:
    data["definitions"][0]["set_cd_bit"] = True
if recursive:
    data["definitions"][0]["set_rd_bit"] = True
else:
    data["definitions"][0]["set_rd_bit"] = False
data["definitions"][0]["protocol"] = protocol
if verbose and machine_readable:
    usage("Specify verbose *or* machine-readable output")
    sys.exit(1)
if (display_probes or display_resolvers or display_rtt) and machine_readable:
    usage("Display probes/resolvers/RTT *or* machine-readable output")
    sys.exit(1)

if nameserver is None:
    nameservers = [None,]

for nameserver in nameservers:
    data["probes"][0]["tags"] = {}
    if nameserver is None:
        data["definitions"][0]["use_probe_resolver"] = True
        # Exclude probes which do not have at least one working resolver
        data["probes"][0]["tags"]["include"] = ["system-resolves-a-correctly",
                                                "system-resolves-aaaa-correctly"] 
    else:
        data["probes"][0]["tags"]["include"] = []
        data["definitions"][0]["use_probe_resolver"] = False
        data["definitions"][0]["target"] = nameserver
        data["definitions"][0]["description"] += (" via nameserver %s" % nameserver) # TODO if several nameservers, they addresses are added after each other :-( 
    if ip_family == 6:
        data["probes"][0]["tags"]["include"].append("system-ipv6-works")
    else:
        data["probes"][0]["tags"]["include"].append("system-ipv4-works")
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

        if not machine_readable and verbose:
            print "Measurement #%s for %s/%s uses %i probes" % \
            (measurement.id, domainname, qtype, measurement.num_probes)

        old_measurement = measurement.id
        results = measurement.results(wait=True)
    else:
        measurement = RIPEAtlas.Measurement(data=None, id=measurement_id)
        results = measurement.results(wait=False)
        if verbose:
            print "%i results from already-done measurement %s" % (len(results), measurement.id)

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
        first_error = ""
        probe_resolves = False
        resolver_responds = False
        all_timeout = True
        if result.has_key("result"):
            result_set = [{'result': result['result']},]
        elif result.has_key("resultset"):
            result_set = result['resultset']
        elif result.has_key("error"):
            result_set = []
            myset = []
            if result['error'].has_key("timeout"):
                myset.append("TIMEOUT")
            elif result['error'].has_key("socket"):
                all_timeout = False
                myset.append("NETWORK PROBLEM WITH RESOLVER")
            else:
                all_timeout = False
                myset.append("NO RESPONSE FOR UNKNOWN REASON at probe %s" % probe_id)
        else:
            raise RIPEAtlas.WrongAssumption("Neither result not resultset member")
        if len(result_set) == 0:
            myset.sort()
            set_str = " ".join(myset)
            sets[set_str].total += 1
            if display_probes:
                if probes_sets.has_key(set_str):
                    probes_sets[set_str].append(probe_id)
                else:
                    probes_sets[set_str] = [probe_id,]
        for result_i in result_set:
            try:
                if result_i.has_key("dst_addr"):
                    resolver = str(result_i['dst_addr'])
                elif result_i.has_key("dst_name"): # Apparently, used when there was a problem
                    resolver = str(result_i['dst_name'])
                elif result.has_key("dst_addr"): # Used when specifying a name server
                    resolver = str(result['dst_addr'])
                elif result.has_key("dst_name"): # Apparently, used when there was a problem
                    resolver = str(result['dst_name'])
                else:
                    resolver = "UNKNOWN RESOLUTION ERROR"
                myset = []
                if not result_i.has_key("result"):
                    if only_one_per_probe:
                        continue
                    else:
                        if result_i['error'].has_key("timeout"):
                            myset.append("TIMEOUT")
                        elif result_i['error'].has_key("socket"):
                            all_timeout = False
                            myset.append("NETWORK PROBLEM WITH RESOLVER")
                        else:
                            all_timeout = False
                            myset.append("NO RESPONSE FOR UNKNOWN REASON at probe %s" % probe_id)
                else:
                    all_timeout = False
                    resolver_responds = True
                    answer = result_i['result']['abuf'] + "=="
                    content = base64.b64decode(answer)
                    msg = dns.message.from_wire(content)
                    if nsid:
                        for opt in msg.options:
                            if opt.otype == dns.edns.NSID:
                                myset.append("NSID: " + opt.data)
                    successes += 1
                    if msg.rcode() == dns.rcode.NOERROR:
                        probe_resolves = True
                        # If we test an authoritative server, and it returns a delegation, we won't see anything...
                        if result_i['result']['ANCOUNT'] == 0:
                            if verbose:
                                print "Warning: reply at probe %s has no answers: may be the server returned a delegation?" % probe_id
                        for rrset in msg.answer:
                            for rdata in rrset:
                                if rdata.rdtype == qtype_num:
                                    myset.append(string.lower(str(rdata)[0:MAXLEN])) # We truncate because DNSKEY can be very long
                        if display_validation and (msg.flags & dns.flags.AD):
                            myset.append(" (Authentic Data flag) ")
                        if (msg.flags & dns.flags.TC):
                            myset.append(" (TRUNCATED May have to use --ednssize) ")
                    else:
                        if msg.rcode() == dns.rcode.REFUSED: # Not SERVFAIL since
                            # it can be legitimate (DNSSEC problem, for instance)
                            if only_one_per_probe:
                                if first_error == "":
                                    first_error = "ERROR: %s" % dns.rcode.to_text(msg.rcode())
                                continue # Try again
                        else:
                            probe_resolves = True # NXDOMAIN or SERVFAIL are legitimate
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
                if display_rtt:
                    if not result_i.has_key("result"):
                        sets[set_str].rtt +=  result_i['rt']
                    else:
                        sets[set_str].rtt +=  result_i['result']['rt']
            except dns.name.BadLabelType:
                if not machine_readable:
                    print "Probe %s failed (bad label in name)" % probe_id
            except dns.message.TrailingJunk:
                if not machine_readable:
                    print "Probe %s failed (trailing junk)" % probe_id
            except dns.exception.FormError:
                if not machine_readable:
                    print "Probe %s failed (malformed DNS message)" % probe_id
            if only_one_per_probe:
                    break
        if not probe_resolves and first_error != "" and verbose:
            print "Warning, probe %s has no working resolver (first error is \"%s\")" % (probe_id, first_error)
        if not resolver_responds:
            if all_timeout:
                if verbose:
                    print "Warning, probe %s never got reply from any resolver" % (probe_id)
                # TODO these results appear as duplicate(s)
                set_str = "TIMEOUT(S)"
            else:
                myset.sort()
                set_str = " ".join(myset)
            sets[set_str].total += 1
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
        if display_rtt:
            detail += "Average RTT %i ms" % (sets[myset].rtt/sets[myset].total)
        if not machine_readable:
            print "[%s] : %i occurrences %s" % (myset, sets[myset].total, detail)
        else:
            details.append("[%s];%i" % (myset, sets[myset].total))

    if not machine_readable:
        print ("Test #%s done at %s" % (measurement.id, time.strftime("%Y-%m-%dT%H:%M:%SZ", measurement.time)))
        print ""
    else:
        # TODO: what if we analyzed an existing measurement?
        if nameserver is None:
            ns = "DEFAULT RESOLVER"
        else:
            ns = nameserver
        print ",".join([domainname, qtype, str(measurement.id), "%s/%s" % (len(results), measurement.num_probes), \
                        time.strftime("%Y-%m-%dT%H:%M:%SZ", measurement.time), ns] + details)
