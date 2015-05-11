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

class Message:
    """Object to store nagios messages"""
    def __init__(self, verbose):
        """
        Initialise Object
        verbose is an interger indicating how Much information to return
        """
        #need to group these by probe id
        self.error = []
        self.warn = []
        self.ok = []
        self.verbose = verbose

    def add_error(self, message):
        """Add an error message"""
        self.error.append(message)

    def add_warn(self, message):
        """Add an warn message"""
        self.warn.append(message)

    def add_ok(self, message):
        """Add an ok message"""
        self.ok.append(message)

    def str_message(self, probe_messages):
        return ', '.join(['%s=%s' % (key, value) for (key, value) in probe_messages.items()])

    def exit(self):
        """Parse the message and exit correctly for nagios"""
        if len(self.error) > 0:
            if self.verbose > 0:
                print "ERROR: %d: %s" % (len(self.error), self.str_message(self.error))
                if self.verbose > 1:
                    print "WARN: %d: %s" % (len(self.warn), self.str_message(self.warn))
                    print "OK: %d: %s" % (len(self.ok), self.str_message(self.ok))

            else:
                print "ERROR: %d" % len(self.error)
            sys.exit(2)
        elif len(self.warn) > 0:
            if self.verbose > 0:
                print "WARN: %d: %s" % (len(self.warn), self.str_message(self.warn))
                if self.verbose > 1:
                    print "OK: %d: %s" % (len(self.ok), self.str_message(self.ok))
            else:
                print "WARN: %d" % len(self.warn)
            sys.exit(1)
        else:
            if self.verbose > 1:
                print "OK: %d: %s" % (len(self.ok), self.str_message(self.ok))
            else:
                print "OK: %d" % len(self.ok)
            sys.exit(0)

class ProbeMessage:
    """Object to store nagios messages"""
    def __init__(self, verbose):
        """
        Initialise Object
        verbose is an interger indicating how Much information to return
        """
        #need to group these by probe id
        self.error = dict()
        self.warn = dict()
        self.ok = dict()
        self.verbose = verbose

    def add_error(self, probe, message):
        """Add an error message"""
        try:
            self.error[probe].append(message)
        except KeyError:
            self.error[probe] = [message]

    def add_warn(self, probe, message):
        """Add an warn message"""
        try:
            self.warn[probe].append(message)
        except KeyError:
            self.warn[probe] = [message]

    def add_ok(self, probe, message):
        """Add an ok message"""
        try:
            self.ok[probe].append(message)
        except KeyError:
            self.ok[probe] = [message]

    def str_message(self, probe_messages):
        return ', '.join(['%s=%s' % (key, value) for (key, value) in probe_messages.items()])

    def exit(self, args):
        """Parse the message and exit correctly for nagios"""
        if len(self.error) >= args.crit_probes:
            len(self.error)
            if self.verbose > 0:
                print "ERROR: %d: %s" % (len(self.error), self.str_message(self.error))
                if self.verbose > 1:
                    print "WARN: %d: %s" % (len(self.warn), self.str_message(self.warn))
                    print "OK: %d: %s" % (len(self.ok), self.str_message(self.ok))

            else:
                print "ERROR: %d" % len(self.error)
                print "WARN: %d" % len(self.warn)
                print "OK: %d" % len(self.ok)
            sys.exit(2)
        elif len(self.error) >= args.warn_probes:
            if self.verbose > 0:
                print "ERROR: %d: %s" % (len(self.error), self.str_message(self.error))
                if self.verbose > 1:
                    print "WARN: %d: %s" % (len(self.warn), self.str_message(self.warn))
                    print "OK: %d: %s" % (len(self.ok), self.str_message(self.ok))

            else:
                print "ERROR: %d" % len(self.error)
                print "WARN: %d" % len(self.warn)
                print "OK: %d" % len(self.ok)
            sys.exit(1)
        elif len(self.warn) >= args.warn_probes:
            if self.verbose > 0:
                print "WARN: %d: %s" % (len(self.warn), self.str_message(self.warn))
                print "ERROR: %d: %s" % (len(self.error), self.str_message(self.error))
                if self.verbose > 1:
                    print "OK: %d: %s" % (len(self.ok), self.str_message(self.ok))
            else:
                print "WARN: %d" % len(self.warn)
                print "OK: %d" % len(self.ok)
                print "ERROR: %d" % len(self.error)
            sys.exit(1)
        else:
            if self.verbose > 1:
                print "OK: %d: %s" % (len(self.ok), self.str_message(self.ok))
                print "WARN: %d: %s" % (len(self.warn), self.str_message(self.warn))
                print "ERROR: %d: %s" % (len(self.error), self.str_message(self.error))
            else:
                print "OK: %d" % len(self.ok)
                print "WARN: %d" % len(self.warn)
                print "ERROR: %d" % len(self.error)
            sys.exit(0)

