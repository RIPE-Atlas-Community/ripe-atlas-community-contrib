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

import sys
import time
import argparse
import requests
import json
import pprint
from ripe.atlas.sagan import Result, ResultParseError

class Measurment:
    '''Parent object for an atlas measurment'''
    parsed = None
    probe_id = None
    parse_error = False
    msg = "%s (%s)"

    def __init__(self, probe_id, payload):
        '''Initiate generic message data'''
        self.probe_id = probe_id
        self.payload = payload
        try:
            self.parsed = Result(payload).get(payload, on_error=Result.ACTION_IGNORE)
            #self.parsed = self.parsed.get(payload)
        except ResultParseError as e:
            self.parse_error = e


    @staticmethod
    def add_args(parser):
        '''add arguments'''
        parser.add_argument('-v', '--verbose', action='count',
                help='Increase verbosity')
        parser.add_argument("measurement_id",
                help="Measuerment ID to check")
        parser.add_argument('-w', '--warn-probes', type=int, default=2,
                help='WARN if # probes have a warn condition')
        parser.add_argument('-c', '--crit-probes', type=int, default=1,
                help='ERROR if # probes have a warn condition')
        parser.add_argument('-k', '--key',
                help="API key for non-public measurements")
        parser.add_argument('--max_measurement_age', type=int, default=3600,
                help='The max age of a measuerment in seconds')

    def ensure_list(self, list_please):
        '''make @list_please a list if it isn't one already'''
        if type(list_please) != list:
            return [(list_please)]
        else:
            return list_please

    def check_measurement_age(self, max_age, message):
        '''Check if a measerment is fresh enough'''
        min_time = time.time() - max_age
        if self.payload["timestamp"] < min_time:
            message.add_error(self.probe_id, "measurement to old: {}".format(self.parsed.created))
        else:
            message.add_ok(self.probe_id, "measurement fresh: {}".format(self.parsed.created))

    def check_string(self, check_string, measurment_string,
            check_type, message):
        '''Generic check to compare two strings'''
        msg = '{}: {} ({})'.format(check_type, measurment_string, check_string)
        if str(check_string) == str(measurment_string):
            message.add_ok(self.probe_id, msg)
        else:
            message.add_error(self.probe_id, msg)


    def check(self, args, message):
        '''main check fucntion'''
        self.check_measurement_age(args.max_measurement_age, message)


class MeasurmentSSL(Measurment):
    '''Object for an atlas SSL Measurment'''

    def __init__(self, probe_id, payload):
        '''Initiate object'''
        #super(Measurment, self).__init__(payload)
        Measurment.__init__(self, probe_id, payload)
        if not self.parse_error:
            self.common_name = self.parsed.certificates[0].subject_cn
            self.expire = self.parsed.certificates[0].valid_until
            self.sha1 = self.parsed.certificates[0].checksum_sha1

    @staticmethod
    def add_args(subparser):
        '''add SSL arguments'''
        parser = subparser.add_parser('ssl', help='SSL check')
        Measurment.add_args(parser)
        parser.add_argument('--common-name',
                help='Ensure a cert has this cn')
        parser.add_argument('--ssl-expire-days', type=int, default=30,
                help="Ensure certificate dosne't expire in x days")
        parser.add_argument('--sha1hash',
                help="Ensure certificate has this sha1 hash")

    def check_expiry(self, warn_expiry, message):
        '''Check if the certificat is going to expire before warn_expiry'''
        current_time = time.time()
        warn_time = current_time + (warn_expiry * 60 * 60 * 24)
        if float(self.expire.strftime("%s")) < current_time:
            message.add_error(self.probe_id, self.msg % (
                    "certificate expierd", self.expire))
            return
        elif float(self.expire.strftime("%s")) < warn_time:
            message.add_warn(self.probe_id, self.msg % (
                    "certificate expires soon", self.expire))
        else:
            message.add_ok(self.probe_id, self.msg % (
                    "certificate expiry good", self.expire))

    def check(self, args, message):
        '''Main SSL check routine'''
        if self.parse_error:
            message.add_error(self.probe_id, self.msg % (
                    'GENRAL',self.parse_error))
        else:
            Measurment.check(self, args, message)
            if args.sha1hash:
                self.check_string( args.sha1hash,
                        self.sha1, 'sha1hash', message)
            if args.common_name:
                self.check_string( args.common_name,
                        self.common_name, 'cn', message)
            if args.ssl_expire_days:
                self.check_expiry(args.ssl_expire_days, message)


class MeasurmentPing(Measurment):
    '''Object for an atlas Ping Measurment'''

    def __init__(self, probe_id, payload):
        '''Initiate object'''
        #super(Measurment, self).__init__(self, payload)
        Measurment.__init__(self, probe_id, payload)

    @staticmethod
    def add_args(subparser):
        '''add SSL arguments'''
        parser = subparser.add_parser('ping', help='SSL check')
        Measurment.add_args(parser)
        parser.add_argument('--rtt-max', type=float,
                help='Ensure the max ttl is below this')
        parser.add_argument('--rtt-min', type=float,
                help='Ensure the min ttl is below this')
        parser.add_argument('--rtt-avg', type=float,
                help='Ensure the avg ttl is below this')

    def check_rtt(self, check_type, rtt, message):
        '''Check the return trip time islower then rtt'''
        msg = "desired (%s), real (%s)" % (rtt, self.parsed.rtt_average)
        if self.parsed.rtt_average < float(rtt):
            message.add_ok(self.probe_id, self.msg % (
                     msg, "Ping %s" % check_type))
        else:
            message.add_error(self.probe_id, self.msg % (
                    msg, "Ping %s" % check_type))

    def check(self, args, message):
        '''Main ping check routine'''
        if self.parse_error:
            message.add_error(self.probe_id, self.msg % (
                    'GENRAL',self.parse_error))
        else:
            Measurment.check(self, args, message)

            if args.rtt_min:
                self.check_rtt("min", args.rtt_min, message)
            if args.rtt_max:
                self.check_rtt("max", args.rtt_max, message)
            if args.rtt_avg:
                self.check_rtt("avg", args.rtt_avg, message)


class MeasurmentHTTP(Measurment):
    '''Object for an atlas HTTP Measurment'''

    def __init__(self, probe_id, payload):
        '''Initiate object'''
        #super(Measurment, self).__init__(self, payload)
        Measurment.__init__(self, probe_id, payload)
        if not self.parse_error:
            self.status = self.parsed.responses[0].code

    @staticmethod
    def add_args(subparser):
        '''add SSL arguments'''
        parser = subparser.add_parser('http', help='SSL check')
        Measurment.add_args(parser)
        parser.add_argument('--status-code', type=int, default=200,
                help='Ensure the site returns this status code')

    def check_status(self, check_status, message):
        '''check the HTTP status is the same as check_status'''
        msg = "desired (%s), real (%s)" % \
                (check_status, self.status)
        try:
            if int(self.status) == int(check_status):
                message.add_ok(self.probe_id, self.msg % (
                    msg, "HTTP Status Code"))
            else:
                message.add_error(self.probe_id, self.msg % (
                    msg, "HTTP Status Code"))
        except ValueError:
            message.add_error(self.probe_id, self.msg % (
                    msg, "HTTP Status Code"))

    def check(self, args, message):
        '''Main HTTP check routine'''
        if self.parse_error:
            message.add_error(self.probe_id, self.msg % (
                    'GENRAL',self.parse_error))
        else:
            Measurment.check(self, args, message)
            if args.status_code:
                self.check_status(args.status_code, message)

class MeasurmentDns(Measurment):
    '''Parent class for a dns measuerment'''
    rcode = None
    questions = []
    answers = []
    authorities = []
    additionals = []
    nsid = None

    def __init__(self, probe_id, payload):
        '''Initiate Object'''
        #super(Measurment, self).__init__(self, payload)
        Measurment.__init__(self, probe_id, payload)
        if not self.parse_error and len(self.parsed.responses) > 0:
            self.questions = self.parsed.responses[0].abuf.questions
            self.answers = self.parsed.responses[0].abuf.answers
            self.authorities = self.parsed.responses[0].abuf.authorities
            self.additionals = self.parsed.responses[0].abuf.additionals
            self.rcode = self.parsed.responses[0].abuf.header.return_code
            self.aa = self.parsed.responses[0].abuf.header.aa
            self.rd = self.parsed.responses[0].abuf.header.rd
            self.ra = self.parsed.responses[0].abuf.header.ra
            self.ad = self.parsed.responses[0].abuf.header.ad
            self.cd = self.parsed.responses[0].abuf.header.cd
            if self.parsed.responses[0].abuf.edns0:
                for opt in self.parsed.responses[0].abuf.edns0.options:
                    if opt.nsid:
                        self.nsid = opt.nsid 

    @staticmethod
    def add_args(parser):
        '''add default dns args'''
        Measurment.add_args(parser)

        parser.add_argument('--aa', action='store_true', help='Response must have AA flag')
        parser.add_argument('--rd', action='store_true', help='Response must have RD flag')
        parser.add_argument('--ra', action='store_true', help='Response must have RA flag')
        parser.add_argument('--ad', action='store_true', help='Response must have AD flag')
        parser.add_argument('--cd', action='store_true', help='Response must have CD flag')
        parser.add_argument('--rcode', default='NOERROR', help='rcode to expect')
        parser.add_argument('--nsid', help='the nsid to expect')


    def check_rcode(self, rcode, message):
        '''Check the RCODE is the same as rcode'''
        msg = "desired (%s), real (%s)" % ( rcode, self.rcode)
        if self.rcode == rcode:
            message.add_ok(self.probe_id, msg)
        else:
            message.add_error(self.probe_id, msg)

    def check(self, args, message):
        '''Main Check routine'''
        self.check_rcode(args.rcode, message)
        Measurment.check(self, args, message)
        if self.parse_error:
            message.add_error(self.probe_id, self.msg % (
                    'GENRAL',self.parse_error))
        else:
            if args.nsid:
                if not self.nsid:
                    message.add_error(self.probe_id, 'no nsid recived')
                elif args.nsid != self.nsid:
                    message.add_error(self.probe_id, 'nsid mismatch: {}!={}'.format(
                        args.nsid, self.nsid))
            if args.aa and not self.aa:
                message.add_error(self.probe_id, 'AA Flag not set')
            if args.rd and not self.rd:
                message.add_error(self.probe_id, 'RD Flag not set')
            if args.ra and not self.ra:
                message.add_error(self.probe_id, 'RA Flag not set')
            if args.ad and not self.ad:
                message.add_error(self.probe_id, 'AD Flag not set')
            if args.cd and not self.cd:
                message.add_error(self.probe_id, 'CD Flag not set')


class MeasurmentDnsA(MeasurmentDns):
    '''class for a dns A measuerment'''

    def __init__(self, probe_id, payload):
        '''Initiate Object'''
        #super(Measurment, self).__init__(self, payload)
        MeasurmentDns.__init__(self, probe_id, payload)

    @staticmethod
    def add_args(subparser):
        parser = subparser.add_parser('A', help='A DNS check')
        MeasurmentDns.add_args(parser)
        parser.add_argument('--answer',
                help='Ensure the RR set from the answer \
                        contains a this string can also check if we get a cname')

    def check(self, args, message):
        if not self.parse_error:
            MeasurmentDns.check(self, args, message)
            for answer in self.answers:
                if answer.type == 'RRSIG':
                    continue
                elif answer.type != 'A' and answer.type != 'CNAME':
                    message.add_error(self.probe_id, self.msg % (
                        'RRTYPE', answer.type))
                elif args.answer:
                    self.check_string( args.answer, answer.address, 'address', message)

class MeasurmentDnsAAAA(MeasurmentDns):
    '''class for a dns AAAA measuerment'''

    def __init__(self, probe_id, payload):
        '''Initiate Object'''
        #super(Measurment, self).__init__(self, payload)
        MeasurmentDns.__init__(self, probe_id, payload)

    @staticmethod
    def add_args(subparser):
        parser = subparser.add_parser('AAAA', help='AAAA DNS check')
        MeasurmentDns.add_args(parser)
        parser.add_argument('--answer',
                help='Ensure the RR set from the answer \
                        contains a CNAME record with this string')

    def check(self, args, message):
        if not self.parse_error:
            MeasurmentDns.check(self, args, message)
            for answer in self.answers:
                if answer.type == 'RRSIG':
                    continue
                elif answer.type != 'AAAA' and answer.type != 'CNAME':
                    message.add_error(self.probe_id, self.msg % (
                        'RRTYPE', answer.type))
                elif args.answer:
                    self.check_string( args.answer, answer.address, 'address', message)

class MeasurmentDnsCH(MeasurmentDns):
    '''class for a dns AAAA measuerment'''

    def __init__(self, probe_id, payload):
        '''Initiate Object'''
        #super(Measurment, self).__init__(self, payload)
        MeasurmentDns.__init__(self, probe_id, payload)

    @staticmethod
    def add_args(subparser):
        parser = subparser.add_parser('CH', help='CH DNS check')
        MeasurmentDns.add_args(parser)
        parser.add_argument('--hostname-bind',
                help='Ensure the RR set from the answer \
                        contains a CNAME record with this string')
        parser.add_argument('--version-bind',
                help='Ensure the RR set from the answer \
                        contains a CNAME record with this string')
        parser.add_argument('--id-server',
                help='Ensure the RR set from the answer \
                        contains a CNAME record with this string')

    def check(self, args, message):
        MeasurmentDns.check(self, args, message)
        if not self.parse_error:
            for answer in self.answers:
                if answer.type == 'RRSIG':
                    continue
                elif answer.type != 'TXT':
                    message.add_error(self.probe_id, self.msg % (
                        'RRTYPE', answer.type))
                else:
                    if args.hostname_bind:
                        self.check_string( args.answer, answer.hostname_bind, 
                                'hostname.bind', message)
                    if args.version_bind:
                        self.check_string( args.answer, answer.version_bind, 
                                'version.bind', message)
                    if args.id_server:
                        self.check_string( args.answer, answer.id_server, 
                                'id.server', message)

class MeasurmentDnsNS(MeasurmentDns):
    '''class for a dns NS measuerment'''

    def __init__(self, probe_id, payload):
        '''Initiate Object'''
        #super(Measurment, self).__init__(self, payload)
        MeasurmentDns.__init__(self, probe_id, payload)

    @staticmethod
    def add_args(subparser):
        parser = subparser.add_parser('NS', help='NS DNS check')
        MeasurmentDns.add_args(parser)
        parser.add_argument('--answer',
                help='Ensure the RR set from the answer \
                        contains a this string can also check if we get a cname')

    def check(self, args, message):
        if not self.parse_error:
            MeasurmentDns.check(self, args, message)
            for answer in self.answers:
                if answer.type == 'RRSIG':
                    continue
                elif answer.type != 'NS':
                    message.add_error(self.probe_id, self.msg % (
                        'RRTYPE', answer.type))
                elif args.answer:
                    self.check_string( args.answer, answer.target, 'target', message)

class MeasurmentDnsMX(MeasurmentDns):
    '''class for a dns MX measuerment'''

    def __init__(self, probe_id, payload):
        '''Initiate Object'''
        #super(Measurment, self).__init__(self, payload)
        MeasurmentDns.__init__(self, probe_id, payload)

    @staticmethod
    def add_args(subparser):
        parser = subparser.add_parser('MX', help='MX DNS check')
        MeasurmentDns.add_args(parser)
        parser.add_argument('--exchange',
                help='Ensure the RR set from the answer \
                        contains a this string')
        parser.add_argument('--pref',
                help='Only check this exhange with this pref, error if we dont see this')

    def check(self, args, message):
        if not self.parse_error:
            MeasurmentDns.check(self, args, message)
            pref_found = False
            for answer in self.answers:
                if answer.type == 'RRSIG':
                    continue
                elif answer.type != 'MX':
                    message.add_error(self.probe_id, self.msg % (
                        'RRTYPE', answer.type))
                else:
                    if args.pref:
                        if int(args.pref) == int(answer.preference):
                            pref_found = True
                        else:
                            continue
                    if args.exchange:
                        self.check_string( args.exchange, answer.mail_exchanger, 
                                'exchange', message)
            if args.pref and not pref_found:
                message.add_error(self.probe_id, 'Pref ({}) not found'.format(args.pref))



class MeasurmentDnsDS(MeasurmentDns):
    '''class for a dns DS measuerment'''
    
    def __init__(self, probe_id, payload):
        '''Initiate Object'''
        #super(Measurment, self).__init__(self, payload)
        MeasurmentDns.__init__(self, probe_id, payload)

    @staticmethod
    def add_args(subparser):
        parser = subparser.add_parser('DS', help='CNAME DS check')
        MeasurmentDns.add_args(parser)
        parser.add_argument('--keytag',
                help='Only check this keytag error if we dont see this')
        parser.add_argument('--algorithm',
                help='Only check this algorithm error if we dont see this')
        parser.add_argument('--digest-type',
                help='Only check this digest type error if we dont see this')
        parser.add_argument('--digest',
                help='Ensure we see this digest')

    def check(self, args, message):
        if not self.parse_error:
            MeasurmentDns.check(self, args, message)
            keytag_found = False
            algorithm_found = False
            digest_type_found = False
            for answer in self.answers:
                if answer.type == 'RRSIG':
                    continue
                elif answer.type != 'DS':
                    message.add_error(self.probe_id, self.msg % (
                        'RRTYPE', answer.type))
                else:
                    if args.keytag:
                        if int(args.keytag) == (answer.tag):
                            keytag_found = True
                        else:
                            continue
                    if args.algorithm:
                        if int(args.algorithm) == int(answer.algorithm):
                            algorithm_found = True
                        else:
                            continue
                    if args.digest_type:
                        if int(args.digest_type) == int(answer.digest_type):
                            digest_type_found = True
                        else:
                            continue
                    if args.digest:
                        self.check_string( args.digest, answer.delegation_key, 
                                'digest', message)
            if args.keytag and not keytag_found:
                message.add_error(self.probe_id, 'Keytag ({}) not found'.format(args.tag))
            if args.algorithm and not algorithm_found:
                message.add_error(self.probe_id, 'Algorithem ({}) not found'.format(args.algorithm))
            if args.digest_type and not digest_type_found:
                message.add_error(self.probe_id, 'Digest Type ({}) not found'.format(args.delegation_key))

class MeasurmentDnsDNSKEY(MeasurmentDns):
    '''class for a dns DNSKEY measurement'''

    def __init__(self, probe_id, payload):
        '''Initiate Object'''
        MeasurmentDns.__init__(self, probe_id, payload)

    @staticmethod
    def add_args(subparser):
        parser = subparser.add_parser('DNSKEY', help='CNAME DNSKEY check')
        MeasurmentDns.add_args(parser)
        parser.add_argument('--dnskey', help='base64 rpresentation of the key')
        parser.add_argument('--dnskey-flags', help='int represting the flags')
        parser.add_argument('--proto', help='int represting the protocol')
        parser.add_argument('--algo', help='int represting the algorithem')

    def check(self, args, message):
        if not self.parse_error:
            MeasurmentDns.check(self, args, message)
            for answer in self.answers:
                if answer.type == 'RRSIG':
                    continue
                elif answer.type != 'DNSKEY':
                    message.add_error(self.probe_id, self.msg % (
                        'RRTYPE', answer.type))
                else:
                    if args.dnskey:
                        dnskey = ''.join(args.dnskey.split())
                        self.check_string( dnskey, answer.key, 'dnskey', message)
                    if args.dnskey_flags:
                        self.check_string( args.dnskey_flags, answer.flags, 
                                'dnskey flags', message)
                    if args.proto:
                        self.check_string( args.proto, answer.protocol, 
                                'dnskey proto', message)
                    if args.algo:
                        self.check_string( args.algo, answer.algorithm, 
                                'dnskey algo', message)

class MeasurmentDnsSOA(MeasurmentDns):
    '''class for a dns SOA measuerment'''
    
    def __init__(self, probe_id, payload):
        '''Initiate Object'''
        #super(Measurment, self).__init__(self, payload)
        MeasurmentDns.__init__(self, probe_id, payload)

    @staticmethod
    def add_args(subparser):
        parser = subparser.add_parser('SOA', help='CNAME SOA check')
        MeasurmentDns.add_args(parser)
        parser.add_argument('--mname',
                help='Ensure the soa has this mname')
        parser.add_argument('--rname',
                help='Ensure the soa has this rname')
        parser.add_argument('--serial',
                help='Ensure the soa has this serial')
        parser.add_argument('--refresh',
                help='Ensure the soa has this refresh')
        parser.add_argument('--expire',
                help='Ensure the soa has this expire')
        parser.add_argument('--nxdomain',
                help='Ensure the soa has this nxdomain')

    def check(self, args, message):
        if not self.parse_error:
            MeasurmentDns.check(self, args, message)
            for answer in self.answers:
                if answer.type == 'RRSIG':
                    continue
                elif answer.type != 'SOA':
                    message.add_error(self.probe_id, self.msg % (
                        'RRTYPE', answer.type))
                else:
                    if args.mname:
                        self.check_string( args.mname, answer.mname, 'mname', message)
                    if args.rname:
                        self.check_string( args.rname, answer.rname, 'rname', message)
                    if args.serial:
                        self.check_string( args.serial, answer.serial, 'serial', message)
                    if args.refresh:
                        self.check_string( args.refresh, answer.refresh, 'refresh', message)
                    if args.expire:
                        self.check_string( args.expire, answer.expire, 'expire', message)
                    if args.nxdomain:
                        self.check_string( args.nxdomain, answer.nxdomain, 'nxdomain', message)


