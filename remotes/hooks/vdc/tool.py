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

def do_ln(vmid,dsid):
  """ print an environment string for the ln command """
  cur.execute("SELECT * FROM datastore_pool where oid = "+str(dsid));
  rows = cur.fetchall()
  if(len(rows)==0):
    print "# No such DS ID: "+str(dsid)
    return

  elements = {}
  xmlParse(elements,ET.fromstring(rows[0]['body']))
  if not elements.has_key('TEMPLATE'):
    print "# DS is missing TEMPLATE parameter"
    return

  if elements['TEMPLATE'].has_key('HOST'):
    print "DS_NAME="+elements['TEMPLATE']['HOST']
  else:
    print "# TEMPLATE is missing HOST parameter"

  cur.execute("SELECT * FROM vm_pool WHERE oid = "+str(vmid));
  rows = cur.fetchall()
  if(len(rows)==0):
    print "# No such VM ID: "+str(vmid)
    return

  elements = {}
  xmlParse(elements,ET.fromstring(rows[0]['body']))

  if not elements.has_key('USER_TEMPLATE'):
    print "# USER_TEMPLATE is missing"
    return

  template = elements['USER_TEMPLATE']

  if template.has_key('VDC_CACHE_LVM'):
    print "CACHE_LVM="+template['VDC_CACHE_LVM']
    print "CACHE_PATH=/dev/"+template['VDC_CACHE_LVM']
  else:
    print "# No VDC_CACHE_LVM parameter"

  
  if template.has_key('VDC_CACHE_SIZE'):
	print "CACHE_SIZE="+template['VDC_CACHE_SIZE']
  else:
    print "# No VDC_CACHE_SIZE parameter"
   
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
  if len(argv) < 4:
    print "Usage: "+argv[0]+" ln <vmid> <dsid>"
    exit(1)
  do_ln(argv[2],argv[3])
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

