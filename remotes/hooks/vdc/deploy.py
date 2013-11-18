#!/usr/bin/python

import xml.etree.ElementTree as ET
from sys import argv

original = ET.parse(argv[1])
params = original.findall(".//disk")
for p in params:
	if p.get('device') == 'disk': p.insert(0,ET.Element("shareable",{}))

original.write(argv[1])
