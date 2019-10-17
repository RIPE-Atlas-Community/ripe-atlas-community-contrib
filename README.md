# RIPE Atlas Community Contrib

(Collection of links to tools and hackathons documentation)

Welcome to the Community Contributions repository! It started as a collection of RIPE Atlas related tools, and developed  into a place to collect the documentation from the various hackathons organised by RIPE NCC. 

In the main repository are contributions by the community of the [RIPE Atlas](https://atlas.ripe.net)
visualizations, tools for analysing measurements data.  

Below are the links to other independantly hosted projects: 

## Projects from the IoT Hackathon Rotterdam 

In October 2019, we held a first [IoT Hackathon, in Rotterdam, next to RIPE79](https://labs.ripe.net/Members/becha/iot-hackathon-at-ripe-79-in-rotterdam ) . We had four teams and four resulting projects: 

* Project “PRAVAG” (Privacy Aware Research of Generic Anomalies and Visualisations) (Anna, Antonios, Grissel, Peter, Petros, Robert, Vasileios) Worked on finding methods to identify network anomalies by analyzing network traffic patterns, for example: detecting malicious device behaviour to prevent/stop i.e. DDoS attacks.
   * Proof of concept : https://github.com/vgiotsas/pargav-iot-hackathon

* Project “Maria” (Anup, Vladislav, Cristel, Marco, Philip, Randy) Added RIPE probe functionality to TTN LoRaWAN Gateway and RPi in general
  * Original code: https://github.com/RIPE-NCC/ripe-atlas-software-probe & more info:   https://atlas.ripe.net/docs/software-probe/
 
* Project “Survival Layer” (Arman, Demian, Desiree, Pouyan, Renan, Tasos) : Goal was to disseminate and authenticate official warnings/alerts in fragmented networks, where users have no access to the broader global Internet: solving it through ICN: information centric networking & Named data networking framework as core ICN (NDN: named-data.net)

* Project “Aethernauts” (Christoph, Craig, Michael, Cristian) Coding an WLAN probe, that should measure WLAN performance indicators, using MicroPython on a ESP32, by befactoring the code to get a better oversight and better maintenace. Including reading config files for variables, which are now hardcoded.
  * https://github.com/zhristoph/wlanprobe 

Here you can find [presentations slides & other documentation] COMING UP 

You can read the [report from the event on RIPE Labs] COMING UP 

## RPKI Deployathon Amsterdam (Routing Security event)

In March 2019, we held a first [RPKI Deployathon in Amsterdam](https://labs.ripe.net/Members/becha/join-the-amsterdam-rpki-deployathon-2019) : an event simmilar to a hackathon, but foocused on BGP routing security. It was organised & supported by RIPE NCC, Juniper NEtworks & Tesuto (Lab). 

Here you can find [presentations slides & other documentation](https://github.com/RIPE-Atlas-Community/ripe-atlas-community-contrib/tree/master/RPKI-deployathon-nl) 

You can read the [report from the event on RIPE Labs](https://labs.ripe.net/Members/antony_stergiopoulos/results-of-the-first-rpki-deployathon). 

## Projects at Quantum Internet Hackathon 

In October 2018, we held a [Quantum Internet Hackahton in Amsterdam](https://labs.ripe.net/Members/becha/join-the-quantum-internet-hackathon-2018): RIPE NCC, QuTech / Quanntum Internet Alliance and Juniper. 

### Main project - adding functionality to SimulaQron 

* Current development tree: https://github.com/SoftwareQuTech/SimulaQron/tree/Develop
  * Not yet merged: https://github.com/SoftwareQuTech/SimulaQron/pulls

* Team aMBiQuouC (Blind Quantum Computation)
  * Project repository: https://github.com/cgmcintyr/SimulaQron 
  * https://github.com/cgmcintyr/SimulaQron/projects/1

* Simple Docker image of SimulaQron

A lot of people had problems installing and starting SimulaQron. Here's a very basic SimulaQron Docker image that runs the default startAll.sh giving you five nodes:  https://hub.docker.com/r/mchackorg/simulaqron/ The ports exposed are 8081--8085. Get it easily with docker pull mchackorg/simulaqron 

* Quantum Disconsensus (Wojciech Kozlowski & team) 
  * https://github.com/RIPE-Atlas-Community/ripe-atlas-community-contrib/blob/master/quantum-internet-hackathon/quantum-disconsensus.md 

* [Quantum Digital Signature (Shota Nagayama & team)](https://github.com/RIPE-Atlas-Community/ripe-atlas-community-contrib/blob/master/quantum-internet-hackathon/quantum-digital-signature.md)

We implement quantum digital signature algorithm on SimulaQron. https://en.wikipedia.org/wiki/Quantum_digital_signature

### Other projects 

* QChat challenges (Team QHamser) 
   https://github.com/mdskrzypczyk/QChat 
  * Project repo+branch: https://github.com/mdskrzypczyk/QChat/tree/hackathon


## Software projects from Network Operators Tools Hackathon 

In June 2018 we had a [Netowrk Operators Tools Hackathon](https://labs.ripe.net/Members/becha/results-hackathon-version-6) in Dublin. All presentation slides are [in the "presentations" directory](https://github.com/RIPE-Atlas-Community/ripe-atlas-community-contrib/tree/master/network-operators-tools-hackathon), and here are the links to the code that was produced during the event: 

* The first group forked the RIPE Atlas tools repository and put it in: https://github.com/kramse/ripe-atlas-tools . In this repo we tracked the quick changes being made during the hackathon, which are documented in the specific presentation we did. The results are a few small Git pull requests and branches while we learned git and python

* BioRouting : https://github.com/bio-routing 

* AS Interdepandancy VIZ: https://github.com/chufia/ASinterdependenceViz

* https://github.com/ripe-stackstorm/go-netconf-refactored & https://github.com/ripe-stackstorm/GoNETCONF 

* https://github.com/ripe-stackstorm 

* with Arista to get telemetry streaming data integrated in OpenNMS: Epic is in our public JIRA for where our Open Source project deals with issues: https://issues.opennms.org/browse/NMS-10223 ; The working branch which is published here: https://github.com/OpenNMS/opennms/tree/jira/NMS-10223 Docs go here: https://wiki.opennms.org/wiki/DevProjects/Telemetry_Arista_EOS

* RuotingDB https://github.com/pgigis/routingdb


## Software projects from Hackathon Version 6 

In November 2017 we had a [Hackathon Version 6](https://labs.ripe.net/Members/becha/results-hackathon-version-6) in Copenhagen. All presentation slides are [in the "slides" directory](https://github.com/RIPE-Atlas-Community/ripe-atlas-community-contrib/tree/master/hackathon-version-6), and here are the links to the code that was produced during the event: 

* “PCAP or it didn’t happen”: ICMPv6 support for libpcap by Matthias Hannig, Moritz Wilhelmy, Daniel Lublin: already merged by the "the-tcpdump-group" ! [1](https://github.com/the-tcpdump-group/libpcap/commit/2c2bcb6b7e0e8358df9aefe3aba03448ecc1fa9b), [2](https://github.com/the-tcpdump-group/libpcap/commit/7d572e74efdbec768a06da9dc2680e838b18b9e8), [3](https://github.com/the-tcpdump-group/libpcap/commit/2bddb7cea8177549bc1c08627d084ce3584b34bf)

* [Pocket Internet](https://github.com/inognet/pocketinternet) by Andy Mindnich, Cristian Sirbu, Evangelos Balaskas, Harry Reeder, Henrik Kramshøj, Samer Lahoud

* [IPvizzz6](https://github.com/TheWildHorse/IPv6TreeMap) & [live version](https://thewildhorse.github.io/IPv6TreeMap/) by Igor Rinkovec, Luuk Hendriks, Nico Heßler, Pedro da Silva Vaz, Thomas Flummer

* [IPv4 and IPv6 Disparities](https://vgiotsas.github.io/ipv6-route-optimization/) & TraceMonks by Andrea Barberio, Baptiste Jonglez, Ioana Livadariu, Nikos Roussos, Petros Gigis, Richard Patterson, Shahin Gharghi, Vasileios Giotsas

* [The Status of IPv6](https://github.com/cteusche-ripencc/status-of-ipv6) by Asbjørn Sloth Tønnesen,  Nico Heßler,  Kristina Hakobyan,  Christoffer Hansen,  Ioana Livadariu & RIPE NCC staff: Christian, Jasper and Steve

## Software projects from DNS Measurements Hackathon 

In April 2017 we had a [DNS Measurements Hackathon](https://labs.ripe.net/Members/becha/results-dns-measurements-hackathon/view) in Amsterdam. All presentation slides are [in the "slides" directory](https://github.com/RIPE-Atlas-Community/ripe-atlas-community-contrib/tree/master/dns-measurements-hackathon), and here are the links to the code that was produced during the event: 

* “Monitoring DNS Propagation Time”, by “Team USA and Friends” {Tom Arnfeld (Cloudflare), Shane Kerr (Dyn), Kai Storbeck (xs4all), Jon Mercereau (ex-LinkedIn) } 
  * Code: https://github.com/tarnfeld/ripe-ncc-hackathon-2017

* “I know what you did…” aka “DNS resolver hijack tester” aka “DNS Censorship” by Edward Zambrano (Spotify), Nick Wolf (consultant), Sergey Krasnopivets (Selectel) , Konstantin Novakovsky (Selectel) }  
  * Code: https://github.com/bigzaqui/ripe-hackaton-apr-2017 

* “DNS Fingerprinting” by “Polish Guys” {Pawel Formski (FarSight Security), Maciej Andzinski (NASK), Marta van der Haagen (design), Mateusz Kaczanowsk (Facebook)} 
  * Documentation: https://recdnsfp.github.io/ 
  * Code: https://github.com/recdnsfp/parsejson 
  * Comments on HackerNews /  YCombinator: https://news.ycombinator.com/item?id=14166467

* Reverse DNS statistics by “RIR team” {Sofia (APNIC, ex-LACNIC), Anand & Max (RIPE NCC), Sara Bagheri (student) } 
  * Code: https://github.com/stucchimax/reverse-dns-stats 
  
* “Everything you ever wanted to know about caching resolvers but were afraid to ask” by Team  “DNSThought” { Andrea Barberio (Facebook), Petros Gigis (RIPE NCC/FORTH), Jerry Lundström (DNS-OARC),  Teemu Rytilahti (HGI, Ruhr-University Bochum), Willem Tooroop (NLNetLabs) } 

  * Slides: https://github.com/DNS-OARC/ripe-hackathon-dns-caching/raw/master/RipeDnsHack17DnsThought.pdf
  * Code: https://github.com/DNS-OARC/ripe-hackathon-dns-caching 
  * https://github.com/DNS-OARC/ripe-hackathon-dns-caching 
  * Demo: http://sg-pub.ripe.net/petros/dnsthought/ 
  * Go bindings for RIPE Atlas API (work in progress) https://github.com/DNS-OARC/ripeatlas 

* “Passive DNS collection (and statistics) from RIPE Atlas Sensors” by Alexandre Dulaunoy (CIRLL.lu) 
  * Code: https://github.com/adulau/passive-dns-atlas 
  * Results:  https://www.foo.be/ripe-atlas/
  * Example:  https://www.foo.be/ripe-atlas/MASTERSERVERNAME.html 

* “Anomaly Detection on DNS Auths” by Team Anomalizers aka Platypus {Christian Doerr (TU Delft)
  Ella Titova (VivaCell), Giovane Moura (SIDN Labs), Jan Harm Kuipers (University of Twente/SIDN Labs), Moritz Mueller (SIDN Labs/University of Twente),  Ricardo Schmidt (University of Twente)   Wouter de Vries (University of Twente) } 
  * Slides: https://github.com/ripe-dns-anomaly/anomalyDetector/blob/master/presentation/presentation.pdf
  * Code: https://github.com/orgs/ripe-dns-anomaly/   
  * Demo: https://ripe-dns-anomaly.github.io
  * Blog: https://www.sidnlabs.nl/a/weblog/ripe-ncc-dns-measurements-hackathon

* “Ripe Atlas Stream To Anywhere” by Team “World Peace” {Ulrich Wisser (IIS), Stefan Jakob (DENIC), } 

## Software projects from IXP-Tools Hackathon 

Software projects created during [IXP-Tools Hackathon](https://atlas.ripe.net/hackathon/ixp-tools/#!the-event) 

* **[PeerMe aka "Make Peering Great Again"](https://github.com/cooperlees/peerme)** (Tool to discover and generate possible peerings between Internet Autonomous Systems) by Cooper Lees, James Paussa & Arnaud Fenioux 

* **[Pinder aka Tinder for Peering](https://github.com/dotwaffle/pinder)** (Swipe Right On A New Peering Relationship)  by Andrea Beccaris, Daniel Quinn, David Barroso, Hannos Adollarsson, Matthew Walster 
  * Site: http://peer.sexy/
  * Slides: http://accel.waffle.sexy/pinder.pdfhttps://peer.sexy/

* **[IXP Valuator](https://github.com/NZRS/IXP-valuator)**, by Sebastian Casto, James Reilly, Flavio Luciani, Khoudia Gueye, Guillermo Cicileo

* Universal Looking Glass aka “One Looking Glass to Rule Them All”: Get MRT data from route collectors worldwide & Display it in familiar Looking Glass style)(e.g. BGPstream from CAIDA , RIPE RIS,  Open BMP  & PCH), by Benedikt Rudolph, Mathias Handsche, Orlin Tenchev, Alexander Ilin & Mikhail Grishin
  * **[back-end](https://github.com/mathias4github/ulg-backend)**
  * **[front-end](https://github.com/mathias4github/ulg-frontend)** 
  * Slides: https://labs.ripe.net/Members/becha/universal-looking-glass-slides/at_download/file
  * Demo / prototype: http://bit.do/universallg

* "Bird's eye":  A Simple Secure Micro Service for Querying Bird 
  * **[Backend - PHP API](https://github.com/inex/birdseye)** by Barry O'Donovan
  * **[Frontend CLI](https://github.com/dfkbg/birdseye)** by Daniel Karrenberg
  * **[Frontend Web](https://github.com/mhannig/birdseye)** by Matthias Hannig
  * **[Go API implementation](https://github.com/mchackorg/birdwatcher)** by Michael Cardell Widerkrantz, Daniel Melani, Jan Paul Dekker. 
  * Live endpoints - INEX Cork production route collectors:
   * 1. http://rc1-cix-ipv4.inex.ie/
   * 2. http://rc1-cix-ipv6.inex.ie/
  * web based consumer http://hannig.cc:8001/birdseye/app/
  * Slides: https://dl.dropboxusercontent.com/u/42407394/2016-10-RIPE73-IXP-Tools/2016-10-RIPE73-IXP-Tools-BirdsEye.pdf

* **["The remote peering Jedi” (Goal: Detecting remote peers at IXPs)](https://github.com/pgigis/remote-peering-jedi)** , by Vasileios Giotsas, Petros Gigis, Alexandros Milolidakis, Eric Nguyen Duy, Marios Isaakidis, Edward Mukasa
  * Slides: https://labs.ripe.net/Members/becha/the-remote-peering-jedi-slides/at_download/file
  * Peering portal: http://inspire.edu.gr/rp/

* **Peer Match-making** (Automate all the things!) by Matthew Stone & Edward Medvedev: https://emedvedev.github.io/peer-matchmaking-web/

## Software projects from [RIPE Atlas Interfaces Hackathon](https://labs.ripe.net/Members/becha/ripe-atlas-interface-hackathon-results)  

* **[Halo](https://github.com/RIPE-Atlas-Community/ripe-atlas-halo)** Halo (Network Outages Dashboard) by Shane Kerr,  Desire Milosevic, Daniel Quinn, 
* **[IP traceroute Explorer](https://github.com/NZRS/IP-traceroute-explorer)** by Sebastian Castro
* **[Geocoded IPv4/IPv6 traceroutes](https://github.com/NZRS/IP-traceroute-explorer/tree/dualtraceipmap)** by Asbjørn Sloth Tønnesen
* **[Detecting Asymmetric Routing over IXPs](https://github.com/inex/ixp-as)** by Jacob Drabczyk, Barry O'Donovan, Drew Taylor  && http://asymcheck.inex.ie/
* "IPv4 versus IPv6 - Who connects faster?" : http://dragon.eecs.jacobs-university.de:5000 by Vaibhav Bajpai 
* **[Tartiflette](https://github.com/4a616d6573205265696c6c79/tartiflette)** Near Real-Time Anomaly Detection from RIPE Atlas Stream by Razan K Abdallah, Randy Bush, Alexandru Manea, Cristel Pelsser, Wenqin Shao, James Reilly
* **[IXP-Country-Jedi 2.0](https://github.com/santiagorr/ixp-country-jedi)** Improvements for IXP-Country-Jedi based on TraIXroute, by Dimitris Mavrommatis, Edwards Mukasa, Gigis Petros, Santiago Ruano Rincón
* **[Traceroutes Streaming](https://github.com/dfkbg/Traceroute-Streaming)** offered by DFK as a project / data 

## Software projects from Tools-for-operators Hackathon 

Software projects created during [Tools Hackathon in November 2015](https://labs.ripe.net/Members/becha/ripe-atlas-tools-hackathon-results): 

*  **[YIN YANG ninjaX traceroute](https://github.com/bigzaqui/yinyang)** by Edward, Orlin, Sascha, Rickard: measuring asymetric paths 
* **[Atlas Shrugd](https://github.com/shane-kerr/ripe-atlas-shrugd)** by Shane & Collin: Emulating DNS resolution using RIPE Atlas
*  **[ASN Tryst](https://github.com/dk379/asn-tryst)** by Martin, Dmitry, Aleksander, James & Christian: An ASN to ASN interconnect viewer 

## Software projects from Dataviz Hackathon

Software projects sreated during [DataViz Hackathon](https://labs.ripe.net/Members/becha/ripe-atlas-hackathon-results) in March 2015: 

* **[Traceroute consistency check](https://github.com/vdidonato/Traceroute-consistency-check)** by Valentino

* **[sBucket](https://github.com/cod3monk/RIPE-Atlas-sbucket)** by Jullian 
 
* **[anycast](https://github.com/tlevine/ripe-atlas-anycast)** by Tom Levine 

* **[anycast-work](https://github.com/shane-kerr/ripe-atlas-anycast-work)** by Shane Kerr 

* **[treetracert](https://github.com/cjdelisle/treetracert)** by CJdeLisle 

* **[R for RIPE Atlas](https://github.com/tlevine/rripe-atlas)** by Tom Levine 

* **[bgp-traceroutes](https://github.com/wires/bgp-traceroutes)** by Jelle Herold 

* **[Ripe Map](https://github.com/opendatacity/ripe-map)** by Michael & Katja 

* **[ZeeRover DNS](https://github.com/USC-NSL/RIPE2015HackAThon)** by Matt Clader & Ruwaifa Anwar 

* **[Disco](https://github.com/merlijntishauser/ripe-hackathon-disco)** by Team Disco 

* **[BGP Atlas Monitor (BAM!)](https://github.com/guedou/bam)** by Guillaume Valadon Francois Contant Mathias Handsche Thomas Holterbach

* **[Probes Flowing Landscape](https://github.com/vinayakh/ripe-atlas-probedis)** Distribution of Ripe Atlas Probes by geo over time, by Vinayak Hegde

* **[DistanceCheck](https://github.com/cod3monk/RIPE-OpenIPMap-distancecheck)** Distance Checking Tool for OpenIPMap Based on RIPE Atlas Traceroute Data

* **[CLI traceroute](https://github.com/emileaben/cmdline-atlas-trace)** Do RIPE Atlas traceroutes on the commandline

* **[Visualizing unsual latencies](https://github.com/darkk/atls-hktn)** Created at the second Russian hackathon on Internet measurements, with the Original goal: measure latency between geographically close points and pinpoint abnormally high latencies (bad peering?) compared to speed of light in fiber.

## RIPE NCC Tools 

* **[Official RIPE Atlas CLI toolset](https://github.com/RIPE-NCC/ripe-atlas-tools/)** Official command-line client for RIPE Atlas *PULL REQUESTS WELCOME!*  

* **[Cousteau](https://github.com/RIPE-NCC/ripe-atlas-cousteau)**: A Python 
  client for RIPE ATLAS API, actively maintained by the RIPE Atlas team.

* **[Sagan](https://github.com/RIPE-NCC/ripe.atlas.sagan)**: A parsing library
  for RIPE Atlas measurement results, actively maintained by the RIPE Atlas team.

* **[DNSMON code](https://github.com/RIPE-NCC/dnsmon/)**: The RIPE NCC DNS Monitoring Service (DNSMON) provides a comprehensive, objective and up-to-date overview of the quality of the service offered by high-level Domain Name System (DNS) servers.

## NCC-staff-personal Tools

* **[RIPE Atlas Command Line Manager](https://github.com/astrikos/ripe-atlas-cmdline)**:
  Provides a command line manager.

* **[Mesh Manager](https://github.com/robert-kisteleki/ripeatlas-meshmanager)** A simple application to manage traceroute meshes with RIPE Atlas.

* **[Connection Streaming](https://github.com/astrikos/atlas-connections-stream)** RIPE ATLAS connection stream simple visualization

* **[IXP Country Jedi](https://github.com/emileaben/ixp-country-jedi)** Set of scripts to measure and analyse countries and/or IXPs using RIPE Atlas

* **[WebGL](https://github.com/danielquinn/RIPE-Atlas-WebGL-Globe-Prototype)**
Experimenting with visualising RIPE Atals measurement data on a WebGL globe.

* **[IXP-country Jedi](http://github.com/emileaben/ixp-country-jedi)** Set of scripts to measure and analyse countries and/or IXPs using RIPE Atlas

* **[OpenIPmap](https://github.com/RIPE-Atlas-Community/openipmap)** Geolocating Internet infrastructure by crowdsourcing

* **[Datacenter latency map](https://github.com/RIPE-Atlas-Community/datacentre-latency-map)** 

* **[LatencyMON](https://github.com/MaxCam/viz-atlas-latencymon)** See latencies measured from a set of RIPE Atlas probes to your service in realtime

* **[Eyeball traceroute](emileaben/eyeballtrace)** Do RIPE Atlas traceroutes from networks with significant user populations in a countr



## Misc Community Tools 

* https://gist.github.com/samerlahoud/f893814265e7534d395000005329cbda#file-anchor-voronoi-cells-py & http://lahoud.fr/anchor-voronoi.html

* Created during LACNIC hackathon: https://github.com/LACNIC/hackathon/tree/master/17%20MVD/entrebagles/RIPE%20Atlas 

* **[Atlas Tools](https://github.com/NullHypothesis/atlas_tools)**: Allows
  you to create measurements, parse JSON-formatted results & select RIPE Atlas
  probes based on their area.

* **[DNSSEC tools](https://github.com/ncanceill/atlas-dnssec)**: A collection of
  tools for performing and analysing DNSSEC measurements with RIPE Atlas.

* **[RIPE Atlas Toolbox](https://github.com/pierdom/atlas-toolbox)**: A collection of
  Perl scripts for managing custom active measurements on the RIPE Atlas network

* **[RIPE Atlas Tracepath](https://github.com/pierky/ripeatlastracepath)**: A 
  Python script/CGI which reads results from RIPE Atlas traceroute measurements
  (both IPv4 and IPv6) and shows the Autonomous Systems toward the target.

* **[USC-NSL's RIPE Atlas scripts](https://github.com/USC-NSL/ripe-atlas)**:
  A set of Python command-line scripts and library for issuing measurements to the RIPE Atlas network.

* **[GoogleEarth visualizaiton for RIPE Atlas traceroutes](https://github.com/mathias4github/ripe-atlas-traceroute2kml)** 
  A Python script which reads results from RIPE Atlas traceroute measurements (both IPv4 and IPv6) and generates a *.kml file.

* **[Rumy gem - API wrapper](https://github.com/EddyShure/ripe-atlas)** "ripe-atlas" is a minimalistic API wrapper for the RIPE Atlas API. It is written entirely in Ruby.
 
* **[Maera](https://github.com/monrad/maera)** 
  Maera is a tool that is able to generate latency maps from RIPE ATLAS data. 
  Some examples: http://monrad.github.io/maera/maera/2015/03/16/welcome-to-maera.html 

* **[Atlas-Blocked](https://github.com/b4ldr/atlas-blocked)**: A project to test 
  if a website is being blocked/filtered by using RIPE Atlas.

* **[Mathematica](https://github.com/stumpy/atlas.ripe.net)** Mathematica utilities to visualize network measurements by atlas.ripe.net probes

* **[SrikanthKS/VisualTrace](https://github.com/SrikanthKS/VisualTrace)** Web based Visual traceroute is an application which plots live traceroute command on Google maps. Our application gets the source and destination from user and submits the traceroute request to a third party internet measurement service, RIPE Atlas REST

* **[interference](https://github.com/nsg-ethz/atlas_interference)** Quantifying interference between measurements on the RIPE Atlas platform

* **[API access in Go](https://github.com/keltia/ripe-atlas)** RIPE Atlas API access in Go.

* **[Interference](https://github.com/nsg-ethz/atlas_interference)** Quantifying interference between measurements on the RIPE Atlas platform 

* **[jAtlasX](https://github.com/de-cix/jAtlasX)** Access RIPE Atlas through Java 

* **[TestNetAnchors](https://github.com/olavmrk/testnet-ripe-anchors)** Test network connectivity by connecting to RIPE Atlas Anchors

* **[RIPE Atlas Monitoring System](https://github.com/Flugstein/ripe-atmos)** testing environment that lets you monitor the connection quality from all over the world to your Server using the RIPE Atlas Network. 

* **[RIPE Atlas Detector](https://github.com/romain-fontugne/ripeAtlasDetector)**  

* **[Ip Topology Map](https://github.com/NZRS/IpTopologyMap)** Using traceroutes generated by RIPE Atlas probes, generates a BGP peering view of the Internet of a set of countries.

* **[ripe-atlas-monitor](https://github.com/pierky/ripe-atlas-monitor)** A tool to monitor results collected by RIPE Atlas probes and verify they match against predefined expected values.

* **[atlas_scavenger](https://github.com/density215/atlas_scavenger)** Read measurements from the RIPE Atlas API and put the in a local postgres database in a jsonb field.

* **[Other CLI tools by ColdHakCA](coldhakca/atlas_tools)** (SSL Measurement, Traceroute data visualization, Maxmind GeoIP data integration) 

* **[RIPE Atlas lowest latency](vincentbernat/ripe-atlas-lowest-latency)** determine the lowest possible latency to reach a set of endpoints 



 


