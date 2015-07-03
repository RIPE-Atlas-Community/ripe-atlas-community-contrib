#!/usr/bin/python

""" Python code to start a RIPE Atlas UDM (User-Defined
Measurement). This one is for running IPv4 or IPv6 traceroute queries
to analyze routing

You'll need an API key in ~/.atlas/auth.

Stephane Bortzmeyer <bortzmeyer@nic.fr>
"""

import json
import time
import os
import string
import sys
import time
import getopt
import socket
import cPickle as pickle

import RIPEAtlas

# If we use --format:
# import cymruwhois

# Default values
country = None # World-wide
asn = None # All
area = None # World-wide
old_measurement = None
verbose = False
requested = 5 # Probes
protocol = "UDP"
percentage_required = 0.9
the_probes = None
format = False

def is_ip_address(str):
    try:
        addr = socket.inet_pton(socket.AF_INET6, str)
    except socket.error: # not a valid IPv6 address
        try:
            addr = socket.inet_pton(socket.AF_INET, str)
        except socket.error: # not a valid IPv4 address either
            return False
    return True

def usage(msg=None):
    if msg:
        print >>sys.stderr, msg
    print >>sys.stderr, "Usage: %s target-IP-address" % sys.argv[0]
    print >>sys.stderr, """Options are:
    --verbose or -v : makes the program more talkative
    --help or -h : this message
    --format or -f : downloads the results and format them in a traditional traceroute way
    --country=2LETTERSCODE or -c 2LETTERSCODE : limits the measurements to one country (default is world-wide)
    --area=AREACODE or -a AREACODE : limits the measurements to one area such as North-Central (default is world-wide)
    --asn=ASnumber or -n ASnumber : limits the measurements to one AS (default is all ASes)
    --probes=N or -s N : selects the probes by giving explicit ID (one ID or a comma-separated list)
    --old_measurement MSMID or - o MSMID : uses the probes of measurement #MSMID
    --requested=N or -r N : requests N probes (default is %s)
    --percentage=X or -p X : stops the program as soon as X %% of the probes reported a result (default is %2.2f)
    """ % (requested, percentage_required)

try:
    optlist, args = getopt.getopt (sys.argv[1:], "fr:c:a:n:o:t:p:vhs:",
                               ["format", "requested=", "country=", "area=", "asn=", "percentage=", "probes=",
                                "protocol=", "old_measurement=", "verbose", "help"])
    for option, value in optlist:
        if option == "--country" or option == "-c":
            country = value
        elif option == "--area" or option == "-a":
            area = value
        elif option == "--asn" or option == "-n":
            asn = value
        elif option == "--old_measurement" or option == "-o":
            old_measurement = value
        elif option == "--protocol" or option == "-t":
            if value.upper() != "UDP" and value.upper() != "ICMP":
                usage("Protocol must be UDP or ICMP")
                sys.exit(1)
            protocol = value.upper()
        elif option == "--probes" or option == "-s":
            the_probes = value # Splitting (and syntax checking...) delegated to Atlas
        elif option == "--percentage" or option == "-p":
            percentage_required = float(value)
        elif option == "--requested" or option == "-r":
            requested = int(value)
        elif option == "--verbose" or option == "-v":
            verbose = True
        elif option == "--format" or option == "-f":
            format = True
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
target = args[0]
if not is_ip_address(target):
    print >>sys.stderr, ("Target must be an IP address, NOT AN HOST NAME")
    sys.exit(1)

data = { "definitions": [
           { "target": target, "description": "Traceroute %s" % target,
           "type": "traceroute", "is_oneoff": True, "protocol": protocol} ],
         "probes": [
             { "requested": requested} ] }
if the_probes is not None:
    if country is not None or area is not None or asn is not None:
        usage("Specify the probes ID *or* country *or* area *or* ASn")
        sys.exit(1)
    data["probes"][0]["type"] = "probes"
    data["probes"][0]["value"] = the_probes
else:
    if country is not None:
        if asn is not None or area is not None or old_measurement is not None:
            usage("Specify country *or* area *or* ASn *or* old measurement")
            sys.exit(1)
        data["probes"][0]["type"] = "country"
        data["probes"][0]["value"] = country
        data["definitions"][0]["description"] += (" from %s" % country)
    elif area is not None:
            if asn is not None or country is not None or old_measurement is not None:
                usage("Specify country *or* area *or* ASn *or* old measurement")
                sys.exit(1)
            data["probes"][0]["type"] = "area"
            data["probes"][0]["value"] = area
            data["definitions"][0]["description"] += (" from %s" % area)
    elif asn is not None:
            if area is not None or country is not None or old_measurement is not None:
                usage("Specify country *or* area *or* ASn *or* old measurement")
                sys.exit(1)
            data["probes"][0]["type"] = "asn"
            data["probes"][0]["value"] = asn
            data["definitions"][0]["description"] += (" from AS #%s" % asn)
    elif old_measurement is not None:
            if area is not None or country is not None or asn is not None:
                usage("Specify country *or* area *or* ASn *or* old measurement")
                sys.exit(1)
            data["probes"][0]["requested"] = 1000 # Dummy value, anyway,
                                                    # but necessary to get
                                                    # all the probes
            # TODO: the huge value of "requested" makes us wait a very long time
            data["probes"][0]["type"] = "msm"
            data["probes"][0]["value"] = old_measurement
            data["definitions"][0]["description"] += (" from probes of measurement #%s" % old_measurement)
    else:
        data["probes"][0]["type"] = "area"
        data["probes"][0]["value"] = "WW"
    
if string.find(target, ':') > -1:
    af = 6
else:
    af = 4
data["definitions"][0]['af'] = af
if verbose:
    print data

measurement = RIPEAtlas.Measurement(data)
print "Measurement #%s %s uses %i probes" % (measurement.id,
                                             data["definitions"][0]["description"],
                                             measurement.num_probes)

rdata = measurement.results(wait=True, percentage_required=percentage_required)
print("%s probes reported" % len(rdata))
print ("Test done at %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
if format: # Code stolen from json2traceroute.py
    from cymruwhois import Client

    def whoisrecord(ip):
        currenttime = time.time()
        ts = currenttime
        if ip in whois:
            ASN,ts = whois[ip]
        else:
            ts = 0
        if ((currenttime - ts) > 36000):
            C = Client()
            ASN = C.lookup(ip)
            whois[ip] = (ASN,currenttime)
        return ASN

    try:
        pkl_file = open('whois.pkl', 'rb')
        whois = pickle.load(pkl_file)
    except IOError:
        whois = {}

    # Create traceroute output
    try:
        for probe in rdata:
            probefrom = probe["from"]
            if probefrom:
                ASN = whoisrecord(probefrom)
                print "From: ",probefrom,"  ",ASN.asn,"  ",ASN.owner
            print "Source address: ",probe["src_addr"]
            print "Probe ID: ",probe["prb_id"]
            result = probe["result"]
            for proberesult in result:
                ASN = {}
                if "result" in proberesult:
                    print proberesult["hop"],"  ",
                    hopresult = proberesult["result"]
                    rtt = []
                    hopfrom = ""
                    for hr in hopresult:
                        if "error" in hr:
                            rtt.append(hr["error"])
                        elif "x" in hr:
                            rtt.append(hr["x"])
                        else:
                            rtt.append(hr["rtt"])
                            hopfrom = hr["from"]
                            ASN = whoisrecord(hopfrom)
                    if hopfrom:
                        print hopfrom,"  ",ASN.asn,"  ",ASN.owner,"  ",
                    print rtt
                else:
                    print "Error: ",proberesult["error"]
            print ""
    finally:
        pkl_file = open('whois.pkl', 'wb')
        pickle.dump(whois, pkl_file)
