#!/usr/bin/python

import MySQLdb
import xml.etree.ElementTree as ET
import os
import sys

hostname = os.uname()[1]

def xmlParse(elements,xml):
  """ parse an XML blob into a hierarchical map """
  for elem in xml:
    if elem.getchildren() == []:
      elements[elem.tag] = elem.text
      continue

    sub = {}
    xmlParse(sub,elem.getchildren())
    if elements.has_key(elem.tag):
      orig = elements[elem.tag]

      if type(orig) <> type([]): orig = [orig]
      sub=[sub]
      elements[elem.tag] = orig+sub
    else:
      elements[elem.tag] = sub

db = MySQLdb.connect(host="nebula",user="oneadmin",passwd="oneadmin",db="opennebula")
cur = db.cursor(MySQLdb.cursors.DictCursor)
cur.execute("FLUSH QUERY CACHE");

output=""
vmid=int(sys.argv[1])
cur.execute("SELECT * FROM vm_pool WHERE oid = '%s'" % vmid)
rows = cur.fetchall()
for row in rows:
  elements = {}
  xmlParse(elements,ET.fromstring(row['body']))
  temp = elements.get('TEMPLATE',None)
  if not temp: continue
  disk = temp.get('DISK',None)
  if not disk: continue
  if type(disk) <> type([]): disk = [disk]
  for d in disk:
    if d['TM_MAD']    <> 'vdc':    continue
    output += "ON_"+d['IMAGE_ID']+"_"+str(vmid)

print 'NAME="%s"' % output
