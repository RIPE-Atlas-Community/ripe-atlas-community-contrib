#!/usr/bin/env python
#
# https://weir.atlas.ripe.net/contrib/active_probes.json
# https://atlas.ripe.net/contrib/active_probes.json
#
# http://www.infornografia.net/atlas/activeprobes.html
# http://www.infornografia.net/atlas/activeprobes.kml
#
# ["U", 52.2956, 4.9387,
#    ["Probe ID", 2,
#     "IPv4 ASN", "<a href='https://stat.ripe.net/AS5615' target='_blank'>5615</a>",
#     "IPv4 Prefix", "<a href='https://stat.ripe.net/82.168.0.0/14' target='_blank'>82.168.0.0/14</a>",
#     "Country Code", "NL",
#     "Up since", "2012-02-20 01:13:10<br>(2 days, 19:27 hrs)"
#     ]
#  ],
#

import json
from xml.dom.minidom import getDOMImplementation
import urllib

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

	# https://atlas.ripe.net/media/map_pin_up.png
	# https://atlas.ripe.net/media/map_pin_up6.png?
	# https://atlas.ripe.net/media/map_pin_down.png

	add_style(doc, doc_el, "probe_up", "http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png")
	add_style(doc, doc_el, "probe_down", "http://maps.google.com/mapfiles/kml/paddle/red-blank.png")
	add_style(doc, doc_el, "probe_up6", "http://maps.google.com/mapfiles/kml/paddle/grn-blank.png")
	url= "https://atlas.ripe.net/contrib/active_probes.json"
	lines= urllib.urlopen(url) 
	line= ' '.join(lines)
	j= json.loads(line)
	for e in j:
		up= e[0]
		lat= e[1]
		lon= e[2]
		a= e[3]
		d={}
		for i in range(0,len(a),2):
			d[a[i]]= a[i+1]
		if "IPv6 Prefix" not in d.keys():
			d["IPv6 Prefix"] = "NA"
		else:
			up= "UP6"
                if "IPv6 ASN" not in d.keys():
                        d["IPv6 ASN"] = "NA"
		else:
                        up= "UP6"
		if "IPv4 Prefix" not in d.keys():
                        d["IPv4 Prefix"] = "NA"
		if "IPv4 ASN" not in d.keys():
                        d["IPv4 ASN"] = "NA"
		if "Country Code" not in d.keys():
                        d["Country Code"] = "NA"
		if "Up since" not in d.keys():
                        d["Up since"] = "NA"
		if "Down since" not in d.keys():
                        d["Down since"] = "NA"
		descr = print_descr(d)
		
		add_probe(doc, doc_el, up, lat, lon, descr)
	print doc.toprettyxml(encoding="UTF-8")

def print_descr(tbl_el):
	table= "<table>"
	table += "<tr><td><b>Probe ID</b></td><td>" + str(tbl_el["Probe ID"]) + "</td>"
	table += "<tr><td><b>IPv4 ASN</b></td><td>" + tbl_el["IPv4 ASN"] + "</td>"
	table += "<tr><td><b>IPv4 Prefix</b></td><td>" + tbl_el["IPv4 Prefix"] + "</td>"
	if tbl_el["IPv6 ASN"] != "NA":
		table += "<tr><td><b>IPv6 ASN</b></td><td>" + tbl_el["IPv6 ASN"] + "</td>"
	if tbl_el["IPv6 Prefix"] != "NA":
		table += "<tr><td><b>IPv6 Prefix</b></td><td>" + tbl_el["IPv6 Prefix"] + "</td>"
	if tbl_el["Country Code"] != "NA":
		table += "<tr><td><b>Country Code</b></td><td>" + tbl_el["Country Code"] + "</td>"
	if tbl_el["Up since"] != "NA":
		table += "<tr><td><b>Up since</b></td><td>" + tbl_el["Up since"] + "</td>"
	if tbl_el["Down since"] != "NA":
        	table += "<tr><td><b>Down since</b></td><td>" + tbl_el["Down since"] + "</td>"
	table += "</table>"
	return str(table)

def add_probe(doc, parent, up, lat_str, lon_str, descr_str):
	place_el = doc.createElement("Placemark")
        parent.appendChild(place_el)

	descr_el = doc.createElement("description")
        place_el.appendChild(descr_el)
	text_node= doc.createCDATASection(str(descr_str))
	descr_el.appendChild(text_node)

	if up == "U":
		styleurl= "#probe_up"
	elif up == "UP6":
		styleurl= "#probe_up6"
	else:
		styleurl= "#probe_down"
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
