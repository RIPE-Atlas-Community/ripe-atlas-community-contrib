#!/usr/bin/env python
#
# https://atlas.ripe.net/contrib/root_anycast.json?msm_id=1&af=6&qst=IS
# https://atlas.ripe.net/contrib/root_anycast.json?msm_id=1&af=4&qst=IS
#
# http://www.infornografia.net/atlas/anycastcheck.html
# http://www.infornografia.net/atlas/anycastcheck.kml
#
# UNK/UNK -> invalid
# inst4 = inst6 -> ok
# inst4 != inst6 -> nok
# inst4 != inst6 (UNK) -> nok-unknowns
# Arguably, nok-unknowns could be set as invalid, as well
#
# ["id_3_31", "52.2985", "4.9375",
#      [
#        "Probe ID", "2 (<a href='https://stat.ripe.net/AS5615' target='_new'>AS5615</a>)",
#        "Instance", "linx",
#        "Reply time", "27 ms",
#        "As of (UTC)", "2012-02-24 13:35:56"
#      ]
# ]

import json
from xml.dom.minidom import getDOMImplementation
import urllib
import re

def xml_newdoc():
        impl= getDOMImplementation()
        newdoc= impl.createDocument(None, "kml", None)
        return newdoc

def main():
	doc= xml_newdoc()
	kml_el= doc.documentElement
	kml_el.setAttribute("xmlns", "http://www.opengis.net/kml/2.2")
	doc_el = doc.createElement("Document")
        kml_el.appendChild(doc_el)

	add_style(doc, doc_el, "chk_ok", "http://maps.google.com/mapfiles/kml/paddle/grn-blank.png")
	add_style(doc, doc_el, "chk_nok", "http://maps.google.com/mapfiles/kml/paddle/pink-blank.png")
	add_style(doc, doc_el, "chk_unknowns", "http://maps.google.com/mapfiles/kml/paddle/pink-circle.png")
	add_style(doc, doc_el, "chk_invalid", "http://maps.google.com/mapfiles/kml/paddle/wht-blank.png")

	probes4= get_probes("4")
	probes6= get_probes("6")
	for probe, list in probes6.iteritems():
		probe_id= probe
		if (probe_id in probes4):
			chk_result= check_instance(probe_id,probes4,probes6)
			descr = print_descr(probe_id,probes4,probes6)
			lat = get_lat(probe_id,probes6)
			lon = get_lon(probe_id,probes6)
			add_probe(doc, doc_el, lat, lon, descr, chk_result)
	print doc.toprettyxml(encoding="UTF-8")

def get_lat(probe_id,probes6):
        data6= {}
        list = probes6[probe_id]
        for i in range(0,len(list),2):
                data6[list[i]]= list[i+1]
	return data6["Latitude"]
	
def get_lon(probe_id,probes6):
        data6= {}
        list= probes6[probe_id]
        for i in range(0,len(list),2):
                data6[list[i]]= list[i+1]
        return data6["Longitude"]

def check_instance(probe_id,probes4,probes6):
	data4= {}
	data6= {}
	list= probes6[probe_id]
	for i in range(0,len(list),2):
		data6[str(list[i])]= str(list[i+1])
	list= probes4[probe_id]
	for i in range(0,len(list),2):
        	data4[str(list[i])]= str(list[i+1])
	if data6["Response"]==data4["Response"]:
		if (data6["Response"] == "UNKNOWN") or (data4["Response"] == "UNKNOWN"):
			result= "invalid"
		else:
			result= "ok"
	elif (data6["Response"] == "UNKNOWN") or (data4["Response"] == "UNKNOWN"):
       		result= "unknowns"
       	else:
		result= "nok"
	return result

def get_probes(af):
	probes= {}
	url= "https://atlas.ripe.net/contrib/root_anycast.json?msm_id=1&af=" + str(af) + "&qst=IS"
        data = json.load(urllib.urlopen(url))
        for probe in data["probes"]:
                items= probe[3]
		# xxx populate items properly
		items.append(str("Latitude"))
		items.append(str(probe[1]))
		items.append(str("Longitude"))
		items.append(str(probe[2]))
                d= {}
                for i in range(0,len(items),2):
                        d[str(items[i])]= str(items[i+1])
		probeid= re.search('^(\d+)',str(d["Probe ID"]))
                probes[str(probeid.group(0))]= items
	return probes

def print_descr(probe_id, probes4, probes6):
        data4= {}
        data6= {}
        list= probes6[probe_id]
        for i in range(0,len(list),2):
                data6[str(list[i])]= str(list[i+1])
        list= probes4[probe_id]
        for i in range(0,len(list),2):
                data4[str(list[i])]= str(list[i+1])
	table= "<table>"
	table += "<tr><td><b>Probe ID:</b></td><td>" + str(data6["Probe ID"]) + "</td></tr>"
	table += "<tr><td><b>Instance (v6):</b></td><td>" + data6["Response"] + " (" + data6["Reply time"] + ")</td></tr>"
	table += "<tr><td><b>Instance (v4):</b></td><td>" + data4["Response"] + " (" + data4["Reply time"] + ")</td></tr>"
	table += "<tr><td><b>As of (UTC):</b></td><td>" + data6["As of (UTC)"] + "</td></tr>"
	table += "</table>"
	return str(table)

def add_probe(doc, parent, lat_str, lon_str, descr_str, result_str):
	place_el = doc.createElement("Placemark")
        parent.appendChild(place_el)

	descr_el = doc.createElement("description")
        place_el.appendChild(descr_el)
	text_node= doc.createCDATASection(str(descr_str))
	descr_el.appendChild(text_node)

	if str(result_str) == "ok":
		styleurl= "#chk_ok"
	elif str(result_str) == "nok":
		styleurl= "#chk_nok"
	elif str(result_str) == "unknowns":
		styleurl= "#chk_unknowns"
	else:
		styleurl= "#chk_invalid"
	styleurl_el = doc.createElement("styleUrl")
        place_el.appendChild(styleurl_el)
	text_node= doc.createTextNode(styleurl)
	styleurl_el.appendChild(text_node)

	point_el = doc.createElement("Point")
        place_el.appendChild(point_el)

	coor_el = doc.createElement("coordinates")
        point_el.appendChild(coor_el)

	lat= float(lat_str)
	lon= float(lon_str)
	text_node= doc.createTextNode("%f,%f,0" % (lon,lat))
	coor_el.appendChild(text_node)

def add_style(doc, parent, name, url):
	style_el= doc.createElement("Style")
	parent.appendChild(style_el)
	style_el.setAttribute("id", name)
	iconstyle_el= doc.createElement("IconStyle")
	style_el.appendChild(iconstyle_el)
	icon_el= doc.createElement("Icon")
	iconstyle_el.appendChild(icon_el)
	href_el= doc.createElement("href")
	icon_el.appendChild(href_el)
	text_node= doc.createTextNode(url)
	href_el.appendChild(text_node)

main()
