<pre>VDC-NEBULA
==========

These scripts provide the glue between OpenNebula and vdc-store. More documentation 
needs to be written but essentially this package needs to be cloned into /var/lib/one
on your NFS server. So, for example;

cd /var/lib/one
mkdir vdc-nebula
cd vdc-nebula
git clone git@github.com:garethbult/vdc-nebula.git

You then need to link this into the tree;

cd /var/lib/one/remotes/datastores
ln -s ../../vdc-nebula/remotes/datastore/vdc
cd /var/lib/one/remotes/tm
ln -s ../../vdc-nebula/remotes/tm/vdc
cd /var/lib/one/remotes/hooks
ln -s ../../vdc-nebula/remotes/hooks/vdc

Make sure you have some sensible permissions set;

cd /var/lib/one/vdc-nebula
chown -R oneadmin:oneadmin .

Then edit /etc/one/oned.conf and add "vdc" to your TM and DATASTORE drivers, for example;

TM_MAD = [
    executable = "one_tm",
    arguments  = "-t 15 -d dummy,lvm,shared,qcow2,ssh,vmfs,iscsi,ceph,vdc" ]

DATASTORE_MAD = [
    executable = "one_datastore",
    arguments  = "-t 15 -d dummy,fs,vmfs,iscsi,lvm,ceph,vdc"]

And as far as the glue is concerned, you're good to go.
- Now you need a couple of patches to substone to give you "vdc" as a datastore type,
- and a working copy of vdc-server and vdc-store.
</PRE>
