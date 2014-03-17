#!/bin/bash
#
# packetloss_graph.sh creates a PNG File for the example:
# retrieve+icmp+periodically+with+crontab+and+write+to+rrd.py
#
# Based on https://calomel.org/rrdtool.html tutorial and graph examples
#
# Daniel Gomez <daniel.gomez@synaix.de>
#

## change directory to the rrdtool script dir
cd /home/user0/ripeatlas
 
## Graph for last 24 hours 
/usr/bin/rrdtool graph packetloss_graph.png \
-w 785 -h 120 -a PNG \
--slope-mode \
--start -86400 --end now \
--font DEFAULT:7: \
--title "Packetloss %" \
--watermark "`date`" \
--vertical-label "Packetloss %" \
--right-axis-label "Packetloss %" \
--lower-limit 0 \
--upper-limit 100 \
--right-axis 1:0 \
--x-grid MINUTE:15:HOUR:1:MINUTE:120:0:%R \
--alt-y-grid --rigid \
DEF:packetlossAS3320=AS3320_latency_db.rrd:plAS3320:AVERAGE \
CDEF:PLNoneAS3320=packetlossAS3320,0,0,LIMIT,UN,UNKN,INF,IF \
CDEF:PL10AS3320=packetlossAS3320,1,10,LIMIT,UN,UNKN,INF,IF \
CDEF:PL25AS3320=packetlossAS3320,10,25,LIMIT,UN,UNKN,INF,IF \
CDEF:PL50AS3320=packetlossAS3320,25,50,LIMIT,UN,UNKN,INF,IF \
CDEF:PL100AS3320=packetlossAS3320,50,100,LIMIT,UN,UNKN,INF,IF \
LINE0:packetlossAS3320#FF8C00:"D-Telekom(%)" \
COMMENT:"pkt loss\:" \
AREA:PLNoneAS3320#FFFFFF:"0%" \
AREA:PL10AS3320#FFFF00:"1-10%" \
AREA:PL25AS3320#FFCC00:"10-25%" \
AREA:PL50AS3320#FF8000:"25-50%" \
AREA:PL100AS3320#FF0000:"50-100%" \
COMMENT:"\s" \
COMMENT:"\s" \

## copy to the web directory
cp packetloss_graph.png /var/www/
