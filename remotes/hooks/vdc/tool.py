#!/usr/bin/python

import MySQLdb
import xml.etree.ElementTree as ET
import os
from syslog import syslog,LOG_INFO
from time import sleep
from sys import argv,exit

hostname = os.uname()[1]

def xmlParse(elements,xml):
  """ parse an XML blob into a hierarchical map """
  for elem in xml:
    if elem.getchildren() <> []:
      elements[elem.tag] = {}
      xmlParse(elements[elem.tag],elem.getchildren())
    else:
      elements[elem.tag] = elem.text

db = MySQLdb.connect(host="127.0.0.1",user="root",passwd="",db="opennebula")
cur = db.cursor(MySQLdb.cursors.DictCursor) 
cur.execute("FLUSH QUERY CACHE");

def Get(table,key,val,keys):
  """ interrogate the XML """
  cur.execute("SELECT * FROM %s where %s = '%s'" % (table,key,val))
  rows = cur.fetchall()
  if(len(rows)==0): return "none"
  elements = {}
  xmlParse(elements,ET.fromstring(rows[0]['body']))
  elements = elements['TEMPLATE']
  keys = keys.split(",")
  for k in keys:
    if elements.has_key(k):
      elements = elements[k]
    else:
      return "none"
  return elements

def do_ln(vmid,dsid,host):
  """ print an environment string for the ln command """
  print "DS_NAME='%s'"         % Get("datastore_pool","oid",str(dsid),"HOST")
  print "CACHE_SIZE='%s'"  % Get("vm_pool","oid",str(vmid),"CONTEXT,VDC_CACHE_SIZE")
  print "CACHE_LVM='%s'"   % Get("host_pool","name",host,"VDC_CACHE_LVM")
  return

def do_add(name,dest,size):
  """ add an entry to the temporary db """
  cur.execute("INSERT INTO vdc (name,path,size) VALUES ('"+name+"','"+dest+"','"+size+"')")
  return

def do_del(name):
  """ check if we need to delete a transient copy """
  cur.execute("SELECT * FROM vdc WHERE name = '"+name+"'")
  rows = cur.fetchall()
  cur.execute("DELETE FROM vdc WHERE name = '"+name+"'")
  if(not len(rows)):
    print "IM_PATH=''"
    return

  print "IM_PATH='"+rows[0]['path']+"'"
  return

if(len(argv)<2):
  print "Usage: ln <vmid> <dsid>"
  exit(1)

if argv[1] == "ln":
  if len(argv) < 5:
    print "Usage: "+argv[0]+" ln <vmid> <dsid> <host>"
    exit(1)
  do_ln(argv[2],argv[3],argv[4])
  exit(0)
elif argv[1] == "add":
  if len(argv)<5:
    print "Usage: "+argv[0]+" add <name> <dir> <size>"
    exit(1)
  do_add(argv[2],argv[3],argv[4])

elif argv[1] == "del":
  if len(argv)<3:
    print "Usage: "+argv[0]+" del <name>"
    exit(1)
  do_del(argv[2])

else:
  print "Unknown command: "+argv[0]
  exit(1)

