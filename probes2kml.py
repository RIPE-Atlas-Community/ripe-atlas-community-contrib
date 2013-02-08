#!/usr/bin/env python
#
# https://weir.atlas.ripe.net/contrib/active_probes.json
#
from sys import stdin
import json
from xml.dom.minidom import getDOMImplementation

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

	add_style(doc, doc_el, "probe_up", "http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png")
	add_style(doc, doc_el, "probe_down", "http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png")

	lines= stdin.readlines()
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
		add_probe(doc, doc_el, up, d["Probe ID"], lat, lon)
	print doc.toprettyxml(encoding="UTF-8")

def add_probe(doc, parent, up, probe_id, lat_str, lon_str):
	place_el = doc.createElement("Placemark")
        parent.appendChild(place_el)

	#name_el = doc.createElement("name")
        #place_el.appendChild(name_el)
	#text_node= doc.createTextNode(str(probe_id))
	#name_el.appendChild(text_node)

	descr_el = doc.createElement("description")
        place_el.appendChild(descr_el)
	text_node= doc.createTextNode("Probe %d" % (probe_id,))
	descr_el.appendChild(text_node)

	if up == "U":
		styleurl= "#probe_up"
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
