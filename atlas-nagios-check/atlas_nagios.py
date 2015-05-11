#!/usr/bin/env python
#Copyright (c) 2014, John Bond <mail@johnbond.org>
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met: 
#
#1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer. 
#2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution. 
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse

from messages import ProbeMessage
from measurements import *
from utils import get_response,get_measurements,check_measurements, parse_measurements

def arg_parse():
    """Parse arguments"""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(
            title="Supported Measuerment types", dest='name')

    #measuerement types
    MeasurmentSSL.add_args(subparsers)
    MeasurmentPing.add_args(subparsers)
    MeasurmentHTTP.add_args(subparsers)
    dns_parser = subparsers.add_parser('dns', help='DNS check')
    dns_subparsers = dns_parser.add_subparsers(
            title="Supported DNS Measuerment types", dest='name')
    MeasurmentDnsA.add_args(dns_subparsers)
    MeasurmentDnsAAAA.add_args(dns_subparsers)
    MeasurmentDnsDS.add_args(dns_subparsers)
    MeasurmentDnsDNSKEY.add_args(dns_subparsers)
    MeasurmentDnsMX.add_args(dns_subparsers)
    MeasurmentDnsNS.add_args(dns_subparsers)
    MeasurmentDnsSOA.add_args(dns_subparsers)

    return parser.parse_args()


def main():
    """main function"""
    args = arg_parse()
    message = ProbeMessage(args.verbose)
    measurements =  get_measurements(args.measurement_id, args.key)
    parsed_measurements = parse_measurements(
            measurements, args.name, message)
    check_measurements(parsed_measurements, args, message)
    if len(measurements) < args.crit_probes:
        print 'ERROR: only recived {} messages'.format(len(measurements))
        sys.exit(2)
    elif len(measurements) < args.warn_probes:
        print 'WARN: only recived {} messages'.format(len(measurements))
        sys.exit(1)
    message.exit(args)


if __name__ == '__main__':
    main()
