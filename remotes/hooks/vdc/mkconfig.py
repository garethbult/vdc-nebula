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
#CONFIG_FILE = "config.temp"
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

images={}
cur.execute("SELECT * FROM vm_pool WHERE state <> 6")
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
    if d['DATASTORE'] <> hostname: continue
    vmid = row['oid']
    imid = d['IMAGE_ID']
    if not images.has_key(imid):
      images[imid]=[vmid]
    else:
      images[imid]=images[imid]+[vmid]

cur.execute("SELECT * FROM datastore_pool WHERE name = '%s'" % hostname)
rows = cur.fetchall()
if( len(rows) <> 1 ):
  print("# ERROR :: needs to be exactly one datastore with name '%s', found %s",hostname,len(rows))
  sys.exit(1)

oid = int(rows[0]['oid'])
while True:

  dst = open(CONFIG_FILE,"w")
  if not dst:
    syslog(LOG_INFO,"* mkconfig ERROR :: config file [%s] is missing" % CONFIG_FILE)
    sys.exit(1)

  syslog(LOG_INFO,"* mkconfig :: Waiting on config file")
  if LockFile(dst): break
  close(dst)
  time.sleep(1)

syslog(LOG_INFO,"* mkconfig :: Processing ...")
dst.truncate()

dst.write("#\n# VDC Config file\n")
dst.write("# AUTO-GENERATED - DO NOT EDIT!\n#\n")
dst.write("[global]\n  host = "+hostname+"\n")
dst.write("  proto = lsfs\n")
dst.write("  path = /var/lib/one/images\n")
dst.write("  size = 10G\n")

cur.execute("SELECT * FROM image_pool")
for row in cur.fetchall():
  elements = {}
  xmlParse(elements,ET.fromstring(row['body']))
  if int(elements['DATASTORE_ID']) <> oid: continue
  persist = int(elements['PERSISTENT'])

  id   = elements.get('ID','0')
  path = elements.get('SOURCE','none')
  temp = elements.get('TEMPLATE',{})
  size = temp.get('CAPACITY','10G')
  used = elements.get('VMS',None)
  if(not used): continue

  for vmid in images.get(id,[]):
    name = "ON_"+str(id)+"_"+str(vmid)
    dst.write("[%s]\n" % name)
    dst.write("  size = %s\n" % size)
    dst.write("  proto = lsfs\n")
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
    dst.write("  path = %s\n" % path)

syslog(LOG_INFO,"* mkconfig :: Unlocking ...")
UnlockFile(dst)
dst.close()
sys.exit(0)
