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
measurement_id = None
verbose = False
requested = 5 # Probes
protocol = "UDP"
percentage_required = 0.9
the_probes = None
format = False
do_lookup = False
do_reverse_lookup = False
size = None
port = None
first_hop = None
max_hops = None

def is_ip_address(str):
    try:
        addr = socket.inet_pton(socket.AF_INET6, str)
    except socket.error: # not a valid IPv6 address
        try:
            addr = socket.inet_pton(socket.AF_INET, str)
        except socket.error: # not a valid IPv4 address either
            return False
    return True

def lookup_hostname(str):
    try:
        info = socket.getaddrinfo(str, 0, socket.AF_UNSPEC, socket.SOCK_STREAM,0, socket.AI_PASSIVE)
        if len(info) > 1:
			print "%s returns more then one IP address please select one" % str
			count=0
			for ip in info:
				count= count + 1	
				fa, socktype, proto, canonname, sa = ip
				print "%s - %s" % (count, sa[0])
			selection=int(raw_input("=>"))
			selection = selection - 1
			selected_ip=info[selection][4][0]
        else:
			selected_ip=info[0][4][0]
			print "Using IP: %s" % selected_ip
    except socket.error:
        return False
    return selected_ip

def lookup_ip(ip):
	try:
		name, alias, addresslist = socket.gethostbyaddr(ip)
	except Exception as e:
		msg = "No PTR"
		return msg
	return name

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
    --old_measurement MSMID or -o MSMID : uses the probes of measurement #MSMID
    --measurement_ID=N or -m N : do not start a measurement, just analyze a former one 
    --requested=N or -r N : requests N probes (default is %s)
    --protocol=PROTO or -t PROTO : uses this protocol (UDP, TCP or ICMP, default is UDP)
    --percentage=X or -p X : stops the program as soon as X %% of the probes reported a result (default is %2.2f)
    --do_lookup : Enables IP lookup feature (default is disabled, may become interactive if the machine has several addresses)
    --do_reverse_lookup or -l : Enables reverse IP lookup feature for hops
    --size=N or -i N : number of bytes in the packet (default unknown)
    --port=N or -b N : destination port for TCP (default is 80)
    --first_hop=N or -d N : TTL/max hop count for the first hop  (default 1)
    --max_hops=N or -x N : TTL/max hop count for the last hop  (default 32)
    """ % (requested, percentage_required)

    """For "TCP Ping"
    <https://labs.ripe.net/Members/wilhelm/measuring-your-web-server-reachability-with-tcp-ping>,
    you need --size=0 --port=$PORT --first_hop=64

    """

try:
    optlist, args = getopt.getopt (sys.argv[1:], "fr:c:a:m:d:x:n:o:t:p:vhdls:i:b:",
                               ["format", "requested=", "country=", "area=", "size=", "port=", "asn=", "percentage=", "probes=",
                                "protocol=", "old_measurement=",  "measurement_ID=", "first_hop=", "max_hops=",
                               "verbose", "help", "do_lookup","do_reverse_lookup"])
    for option, value in optlist:
        if option == "--country" or option == "-c":
            country = value
        elif option == "--area" or option == "-a":
            area = value
        elif option == "--asn" or option == "-n":
            asn = value
        elif option == "--old_measurement" or option == "-o":
            old_measurement = value
        elif option == "--measurement_ID" or option == "-m":
            measurement_id = value
        elif option == "--protocol" or option == "-t":
            if value.upper() != "UDP" and value.upper() != "ICMP" and value.upper() != "TCP":
                usage("Protocol must be UDP or ICMP or TCP")
                sys.exit(1)
            protocol = value.upper()
        elif option == "--probes" or option == "-s":
            the_probes = value # Splitting (and syntax checking...) delegated to Atlas
        elif option == "--percentage" or option == "-p":
            percentage_required = float(value)
        elif option == "--requested" or option == "-r":
            requested = int(value)
        elif option == "--size" or option == "-i":
            size = int(value)
        elif option == "--first_hop" or option == "-d":
            first_hop = int(value)
        elif option == "--max_hops" or option == "-x":
            max_hops = int(value)
        elif option == "--port" or option == "-b":
            port = value
        elif option == "--verbose" or option == "-v":
            verbose = True
        elif option == "--format" or option == "-f":
            format = True
        elif option == "--help" or option == "-h":
            usage()
            sys.exit(0)
        elif option == "--do_lookup" or option == "-d":
            do_lookup = True
        elif option == "--do_reverse_lookup" or option == "-l":
            do_reverse_lookup = True
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

if do_lookup:
    hostname = target
    target = lookup_hostname(hostname)
    if not target:
        print >>sys.stderr, ("Unknown host name \"%s\"" % hostname)
        sys.exit(1)
        
if not is_ip_address(target):
    print >>sys.stderr, ("Target must be an IP address, NOT AN HOST NAME")
    sys.exit(1)

if the_probes is not None:
    requested = len(string.split(the_probes,","))
data = { "is_oneoff": True,
         "definitions": [
           { "target": target, "description": "Traceroute %s" % target,
            "type": "traceroute", "protocol": protocol} ],
            "probes": [
             { "requested": requested} ] }
if size is not None:
    data["definitions"][0]['size'] = size    
if port is not None:
    data["definitions"][0]['port'] = port    
if first_hop is not None:
    data["definitions"][0]['first_hop'] = first_hop
if max_hops is not None:
    data["definitions"][0]['max_hops'] = max_hops    
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
if measurement_id is None:
    if verbose:
        print data

    measurement = RIPEAtlas.Measurement(data)
    print "Measurement #%s %s uses %i probes" % (measurement.id,
                                                 data["definitions"][0]["description"],
                                                 measurement.num_probes)

    rdata = measurement.results(wait=True, percentage_required=percentage_required)
    print("%s probes reported" % len(rdata))
else:
    measurement = RIPEAtlas.Measurement(data=None, id=measurement_id)
    rdata = measurement.results(wait=False)
    if verbose:
            print "%i results from already-done measurement #%s" % (len(rdata), measurement.id)
            
print ("Test #%s done at %s" % (measurement.id, time.strftime("%Y-%m-%dT%H:%M:%SZ", measurement.time)))
if format: # Code stolen from json2traceroute.py
    from cymruwhois import Client

    def whoisrecord(ip):
      try:
	currenttime = time.time()
        ts = currenttime
        if ip in whois:
            ASN,ts = whois[ip]
        else:
            ts = 0
        if ((currenttime - ts) > 36000):
            c = Client()
            ASN = c.lookup(ip)
            whois[ip] = (ASN,currenttime)
        return ASN
      except Exception as e:
	return e
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
		try:
			print "From: ",probefrom,"  ",ASN.asn,"  ",ASN.owner
		except Exception as e:
			print "From: ", probefrom," ","AS lookup error: ",e
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
                            rtt.append(str(hr["x"]))
                        elif "edst" in hr:
                            rtt.append("!")
                        else:
			    try:
                            	rtt.append(hr["rtt"])
                            except KeyError:
				rtt.append("*")
			    hopfrom = hr["from"]
                            ASN = whoisrecord(hopfrom)
                    if hopfrom:
			try:
				if do_reverse_lookup == False:
                        		print hopfrom,"  ",ASN.asn,"  ",ASN.owner,"  ",
		    		else:
					reverse_lookup = lookup_ip(hopfrom)
					print hopfrom,"  ",reverse_lookup,"  ",ASN.asn,"  ",ASN.owner,"  ",
			except Exception as e:
				print "Lookup failed because of", e, "  ",
                    print rtt
                else:
                    print "Error: ",proberesult["error"]
            print ""
    finally:
        pkl_file = open('whois.pkl', 'wb')
        pickle.dump(whois, pkl_file)
