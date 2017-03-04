atlas Nagios
============

Library for preforming various nagios checks using the RIPE Atlas[1] network. 

To use this library you will need to have a current ongoing atlas measurement and know the measurement id.  You should note that this is a work in progress so there are likley errors and almost definetly typos and spelling mistakes.

[1]https://atlas.ripe.net/

Basic Usage
-----------
for supported measuerment types run the following command

atlas-nagios -h 

To get information on what checks are supported run the following

atlas-nagios type -h

some measuerment types will have sub commands, such as the dns check.  to see what these support run the following 

atlas-nagios type subtype -h

Standard checks
---------------

There are a number of parameters that are standard for all check types

####Number of Warning probes
> -w/--warn-probes #of probes

This parameter takes an inteiger and intructes the script to exit with a warning state if # or more probes exit in a warning state.  Warning states are dependent on the check type
 
####Number of criticle probes
> -c/--crit-probes #of probes

This parameter takes an inteiger and intructes the script to exit with a critical state if # or more probes exit in a critical state.  Warning states are dependent on the check type
 
####Key
> -k/--key APIKEY

This is used to pass an API key for measurments that are marked as private.

####Maximum 
> --max_measurement_age #Seconds

This argument takes an int representinf seconds.  If a probes measurment data is older then this value then the probe is considered to be in a critical state

####Verbosity
> -v[v[v]]

This works like a standard -v flag the more you pass the more info you get back.  

DNS Check
---------
There are multible subtypes for the dns check

###Generic arguments
The following argumens are valid for all DNS Checks

####Return Code
> --rcode 'return code string'

This argument expects a sting of the form NOERROR, NXDOMAIN NODATA etc.  if a probe sees an rcode which differes to the argument then the probe is put into a critical state

BUG:This dosn't seem to be working as advertised

####Flags
> --flags comma separated list of flags

This argument expects a commer sperated list of flags of the form RD, AA, AD etc.  if the respose observed by the probe does not contain all flags the probe is put into a critical state. if more flags exist they are ignored

###A record check
This runs checks against an DNS A record measurement

####A Record
> --a-record 192.0.2.1

checks all Answers seen by a probe to ensure that at least one contains the IPv4 address passed.  If this is not the case then the probe is placed in a critical state

####CNAME Record
> --cname-record www.example.com

checks all Answers seen by a probe to ensure that at least one contains the cname passed.  If this is not the case then the probe is placed in a critical state


###AAAA record check
This runs checks against an DNS A record measurement

####A Record
> --aaaa-record 2001:DB8::1

checks all Answers seen by a probe to ensure that at least one contains the IPv6 address passed.  If this is not the case then the probe is placed in a critical state

####CNAME Record
> --cname-record www.example.com

checks all Answers seen by a probe to ensure that at least one contains the cname passed.  If this is not the case then the probe is placed in a critical state

###SOA Record
This runs checks against an DNS SOA record measurement

####MNAME 
> --mname ns.example.com

I the probe sees a different mname then the one passed it is placed into the critical state

####RNAME 
> --mname postmaster.example.com

I the probe sees a different nname then the one passed it is placed into the critical state

####Serial 
> --serial (int)serial number

I the probe sees a different serial then the one passed it is placed into the critical state

####REFRESH 
> --refresh (int)refresh number

I the probe sees a different refresh then the one passed it is placed into the critical state

####UPDATE 
> --update (int)update number

I the probe sees a different update then the one passed it is placed into the critical state

####EXPIRE 
> --expire (int)expire number

I the probe sees a different expire then the one passed it is placed into the critical state

####NXDOMAIN 
> --nxdomian (int)nxdomian number

I the probe sees a different nxdomian then the one passed it is placed into the critical state

###CNAME Record
This runs checks against an DNS CNAME record measurement

####CNAME Record
> --cname-record www.example.com

checks all Answers seen by a probe to ensure that at least one contains the cname passed.  If this is not the case then the probe is placed in a critical state


###DS Record
This runs checks against an DNS DS record measurement

There is a bug in this check, currently dosn't support having multible DS records with different keytags or algorithems

####Key Tag
> --keytag (int)key tag

if the there are any keytags that do not match this value the check is placed into a criticle stage.

####Algorithm
> --algorithm (int)algorithem

if there are any DS records that opserved by a probe that dont contain this algorithem the probe is placed into a criticle state

####Digest type
> --digest-type

if there are any DS records opserved by a probe that dont contain this digest type the probe is placed into a criticle state

####Digest 
> --digest

if there are any DS records opserved by a probe that dont contain this digest the probe is placed into a criticle state

###DNSKEY Record
This runs checks against an DNS DNSKEY record measurement
only the standard checks are implmented

SSL Check
---------
This runs checks against an SSL measurement

####Common name
> --common-name CN

if the CN seen by the atlas probe dose not match this parameter then the probe will be marke in the critical state

####SSL Expiry
> --sslexpiry #days (default: 30 days)

If the expiry seen by the probe is less then the current time + this mount of days then the probe will go into a warning state.  If there certificate sen by the probe has already expired the probe will go into a critical state

####SSL SH1 hash
> --sha1hash Certificat:SHA1:hash

If the sha1 hash seen by the probe is different to the one past the probe will go into a critical state.

Ping Check
----------

This runs checks against an ping measurement

Ping checks are now avalible via the atlas status checks so you might want to consider using this
https://labs.ripe.net/Members/suzanne_taylor_muzzin/introducing-ripe-atlas-status-checks

####Average RTT
> --rtt-avg #ms float

if the average rrt value is lower then this then the probe goes into critical state

####Maximum RTT
> --rtt-max #ms float

Not implmented, currently dose the same as the average RTT

####Minimum RTT
> --rtt-min #ms float

Not implmented, currently dose the same as the average RTT

HTTP Check
----------

This runs checks against an http measurement

Warning this is a restricted check type.  only avalible upon request

####Status Code
> --status-code HTTP status code

If the return code seen by the probe is different to the value passed the probe gose into an critcal state
