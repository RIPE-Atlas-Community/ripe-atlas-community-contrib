#!/usr/bin/python

""" Python code to start a RIPE Atlas UDM (User-Defined
Measurement). This one is to test X.509/PKIX certificates in TLS servers.

You'll need an API key in ~/.atlas/auth.

After launching the measurement, it downloads the results and analyzes
them, displaying the name ("subject" in X.509 parlance) or issuer.

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
import collections

import RIPEAtlas

# https://github.com/pyca/pyopenssl https://pyopenssl.readthedocs.org/en/stable/
import OpenSSL.crypto

# Default values
country = None # World-wide
asn = None # All
area = None # World-wide
verbose = False
requested = 5 # Probes
percentage_required = 0.9
measurement_id = None
display_probes = False
display = "n" #Name
port = 443
ipv6 = False

class Set():
    def __init__(self):
        self.total = 0

def usage(msg=None):
    if msg:
        print >>sys.stderr, msg
    print >>sys.stderr, "Usage: %s target-name-or-IP" % sys.argv[0]
    print >>sys.stderr, """Options are:
    --verbose or -v : makes the program more talkative
    --help or -h : this message
    --issuer or -i : displays the issuer (default is to display the name)
    --key or -k : displays the public key (default is to display the name)
    --serial or -s : displays the serial number (default is to display the name)
    --expiration or -e : displays the expiration datetime (default is to display the name)
    --port or -t : sets the destination port (default is of course 443)
    --displayprobes or -o : display the probes numbers (WARNING: big lists)
    --country=2LETTERSCODE or -c 2LETTERSCODE : limits the measurements to one country (default is world-wide)
    --area=AREACODE or -a AREACODE : limits the measurements to one area such as North-Central (default is world-wide)
    --asn=ASnumber or -n ASnumber : limits the measurements to one AS (default is all ASes)
    --requested=N or -r N : requests N probes (default is %s)
    --percentage=X or -p X : stops the program as soon as X %% of the probes reported a result (default is %2.2f)
    --measurement-ID=N or -m N : do not start a measurement, just analyze a former one
    """ % (requested, percentage_required)

try:
    optlist, args = getopt.getopt (sys.argv[1:], "r:c:a:n:p:om:vhisket:6",
                               ["requested=", "country=", "area=", "asn=", "port=", "percentage=", "measurement-ID",
                                "displayprobes", "ipv6", "verbose", "help", "issuer", "serial", "key"])
    for option, value in optlist:
        if option == "--country" or option == "-c":
            country = value
        elif option == "--area" or option == "-a":
            area = value
        elif option == "--asn" or option == "-n":
            asn = value
        elif option == "--percentage" or option == "-p":
            percentage_required = float(value)
        elif option == "--requested" or option == "-r":
            requested = int(value)
        elif option == "--port" or option == "-t":
            port = int(value)
        elif option == "--measurement-ID" or option == "-m":
            measurement_id = value
        elif option == "--verbose" or option == "-v":
            verbose = True
        elif option == "--ipv6" or option == "-6":
            ipv6 = True
        elif option == "--displayprobes" or option == "-o":
            display_probes = True
        elif option == "--help" or option == "-h":
            usage()
            sys.exit(0)
        elif option == "--issuer" or option == "-i":
            display = "i"
        elif option == "--key" or option == "-k":
            display = "k"
        elif option == "--serial" or option == "-s":
            display = "s"
        elif option == "--expiration" or option == "-e":
            display = "e"
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

if measurement_id is None:
        data = { "is_oneoff": True,
                 "definitions": [
                   { "target": target, "description": "X.509 cert of %s" % target,
                     "type": "sslcert", "port": port} ],
                 "probes": [
                     { "requested": requested} ] }
        if country is not None:
            if asn is not None or area is not None:
                usage("Specify country *or* area *or* ASn")
                sys.exit(1)
            data["probes"][0]["type"] = "country"
            data["probes"][0]["value"] = country
            data["definitions"][0]["description"] += (" from %s" % country)
        elif area is not None:
                if asn is not None or country is not None:
                    usage("Specify country *or* area *or* ASn")
                    sys.exit(1)
                data["probes"][0]["type"] = "area"
                data["probes"][0]["value"] = area
                data["definitions"][0]["description"] += (" from %s" % area)
        elif asn is not None:
                if area is not None or country is not None:
                    usage("Specify country *or* area *or* ASn")
                    sys.exit(1)
                data["probes"][0]["type"] = "asn"
                data["probes"][0]["value"] = asn
                data["definitions"][0]["description"] += (" from AS #%s" % asn)
        else:
            data["probes"][0]["type"] = "area"
            data["probes"][0]["value"] = "WW"
            data["definitions"][0]["description"] += " from the whole world"

        if ipv6:
            data["definitions"][0]['af'] = 6
        else:
            data["definitions"][0]['af'] = 4 

        if verbose:
            print data

        measurement = RIPEAtlas.Measurement(data)
        if verbose:
                print "Measurement #%s to %s uses %i probes" % (measurement.id, target,
                                                            measurement.num_probes)
        rdata = measurement.results(wait=True, percentage_required=percentage_required)
else:
    measurement = RIPEAtlas.Measurement(data=None, id=measurement_id)
    rdata = measurement.results(wait=False)

sets = collections.defaultdict(Set)
if display_probes:
    probes_sets = collections.defaultdict(Set)
print("%s probes reported" % len(rdata))
for result in rdata:
        if display_probes:
            probe_id = result["prb_id"]
        if result.has_key('cert'):
                # TODO: handle chains of certificates
                x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, str(result['cert'][0]))
                detail = ""
                content = x509.get_subject()
                if display == "i":
                    content = x509.get_issuer()
                elif display == "k":
                    key = x509.get_pubkey()
                    # TODO better display of the key
                    content = "%s, type %s, %s bits" % (key, key.type(), key.bits())
                elif display == "s":
                    content = format(x509.get_serial_number(), '05x')
                elif display == "e":
                    if x509.has_expired():
                        detail = " (EXPIRED)"
                    # TODO: better format of the date?
                    content = "%s%s" % (x509.get_notAfter(), detail)
                value = "%s%s" % (content, detail) # TODO better display of the name? https://pyopenssl.readthedocs.org/en/stable/api/crypto.html#x509name-objects
        else:
            if result.has_key('err'):
                error = result['err']
            else:
                error = result['alert']
            value = "FAILED TO GET A CERT: %s" % error
        sets[value].total += 1
        if display_probes:
            if probes_sets.has_key(value):
                probes_sets[value].append(probe_id)
            else:
                probes_sets[value] = [probe_id,]

sets_data = sorted(sets, key=lambda s: sets[s].total, reverse=False)
for myset in sets_data:
    detail = ""
    if display_probes:
        detail = "(probes %s)" % probes_sets[myset]
    print "[%s] : %i occurrences %s" % (myset, sets[myset].total, detail)

print ("Test #%s done at %s" % (measurement.id,
                                time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
