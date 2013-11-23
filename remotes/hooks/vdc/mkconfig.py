#!/usr/bin/python

import MySQLdb
import xml.etree.ElementTree as ET
import os
import sys
import time
import fcntl
from syslog import syslog,LOG_INFO
from time import sleep

CONFIG_FILE = "/etc/vdc/config"
VDC_NAMES = []
hostname = os.uname()[1]

def LockFile(file):
  """ add an advisory lock to a file """
  try:
    fcntl.flock(file.fileno(),fcntl.LOCK_EX)
    return True
  except:
    syslog(LOG_INFO,"* mkconfig :: ERROR locking config file")
    return False

def UnlockFile(file):
  """ remove an advisory lock from a file """
  fcntl.flock(file.fileno(),fcntl.LOCK_UN)

def xmlParse(elements,xml):
  """ parse an XML blob into a hierarchical map """
  for elem in xml:
    if elem.getchildren() <> []:
      elements[elem.tag] = {}
      xmlParse(elements[elem.tag],elem.getchildren())
    else:
      elements[elem.tag] = elem.text

db = MySQLdb.connect(host="nebula",user="oneadmin",passwd="oneadmin",db="opennebula")
cur = db.cursor(MySQLdb.cursors.DictCursor) 
cur.execute("FLUSH QUERY CACHE");

cur.execute("SELECT * FROM datastore_pool");
for row in cur.fetchall():
  elements = {}
  xmlParse(elements,ET.fromstring(row['body']))
  if elements['DS_MAD'] == 'vdc': VDC_NAMES.append(elements['NAME'])

cur.execute("SELECT * FROM vm_pool WHERE state <> 6");
pools = cur.fetchall()

dst = open(CONFIG_FILE,"w")
if not dst:
    syslog(LOG_INFO,"* mkconfig ERROR :: config file [%s] is missing" % CONFIG_FILE)
    sys.exit(1)

syslog(LOG_INFO,"* mkconfig :: Waiting on config file")
while True:
  if LockFile(dst): break
  time.sleep(1)

syslog(LOG_INFO,"* mkconfig :: Processing ...")
dst.truncate()

dst.write("#\n# VDC Config file\n")
dst.write("# AUTO-GENERATED - DO NOT EDIT!\n#\n")
dst.write("[global]\n  host = "+hostname+"\n")
dst.write("  proto = lsfs\n")
dst.write("  path = /var/lib/one/images\n")
dst.write("  size = 10G\n\n")

for row in pools:
  elements = {}
  xmlParse(elements,ET.fromstring(row['body']))
  IMAGE_ID = elements['TEMPLATE']['DISK']['IMAGE_ID']
  cur.execute("SELECT * FROM image_pool WHERE oid = "+str(IMAGE_ID))
  for image in cur.fetchall():
    sub = {}
    xmlParse(sub,ET.fromstring(image['body']))
    if sub.has_key('TEMPLATE'):
      if sub['TEMPLATE'].has_key('CAPACITY'): 
        store = sub['DATASTORE']
        if not store in VDC_NAMES: continue
        if store <> hostname: continue
        store_id = sub['DATASTORE_ID']
        persist = int(sub['PERSISTENT'])
        size = sub['TEMPLATE']['CAPACITY']
        id = str(elements['ID'])
        name = "ON_IM_"+id
        if not persist:
          cur.execute("SELECT * FROM vdc WHERE name = '"+name+"'")
          rows = cur.fetchall()
          if not len(rows):
            sleep(2)
            cur.execute("SELECT * FROM vdc WHERE name = '"+name+"'")
            rows = cur.fetchall()
            # FIXME :: THIS is a timing issue, needs a better fix
            if not len(rows): continue

          row = rows[0]
          path = row['path']
        else:
          path = sub['SOURCE']
 
        dst.write("["+name+"]\n")
        dst.write("  path = " + path+"\n")
        dst.write("  size = " + size + "\n")
        dst.write("  proto = lsfs\n\n")
	
syslog(LOG_INFO,"* mkconfig :: Unlocking ...")
UnlockFile(dst)
dst.close()
sys.exit(0)
