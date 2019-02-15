import subprocess
import shutil
import xml.etree.ElementTree as ET
import shlex
import sys
import os

WORKSHOP_RDP_LOCATION = "workshop_creator_gui_resources/workshop_rdp/"

def printError(message):
    print "\r\n\r\n!!!!!!!!!!\r\nERROR:\r\n", message, "\r\n!!!!!!!!!!\r\n"
    print "Exiting..."
    exit()

def create_rdp_file(directory, filename, ip, port):
	if port:
		ip = ip + ":" + port
		rdp_file_string = \
"""screen mode id:i:0
use multimon:i:0
session bpp:i:16
winposstr:s:0,1,594,106,1394,706
compression:i:1
keyboardhook:i:2
audiocapturemode:i:0
videoplaybackmode:i:1
connection type:i:7
networkautodetect:i:1
bandwidthautodetect:i:1
displayconnectionbar:i:1
enableworkspacereconnect:i:0
disable wallpaper:i:0
allow font smoothing:i:0
allow desktop composition:i:0
disable full window drag:i:0
disable menu anims:i:1
disable themes:i:0
disable cursor setting:i:0
bitmapcachepersistenable:i:1
full address:s:""" + ip + """
audiomode:i:0
redirectprinters:i:1
redirectcomports:i:0
redirectsmartcards:i:1
redirectclipboard:i:1
redirectposdevices:i:0
autoreconnection enabled:i:1
authentication level:i:2
prompt for credentials:i:0
negotiate security layer:i:1
remoteapplicationmode:i:0
alternate shell:s:
shell working directory:s:
gatewayhostname:s:
gatewayusagemethod:i:4
gatewaycredentialssource:i:4
gatewayprofileusagemethod:i:0
promptcredentialonce:i:0
gatewaybrokeringtype:i:0
use redirection server name:i:0
rdgiskdcproxy:i:0
kdcproxyname:s:
	"""
	try:
		print "Creating " + filename + "..."
		if not os.path.exists(directory):
			os.makedirs(directory)
		rdp_file = open(os.path.join(directory,filename), "w+")
		rdp_file.write(rdp_file_string)
		rdp_file.close()
		print "Complete"
	except Exception as e:
		print "ERROR creating RDP File:", e

def create_rdesktop_file(directory, filename, ip, port):
	if port:
		ip = ip + ":" + port
		rdp_file_string = \
"""#!/bin/sh
rdesktop -g 1280x768 -a 16 -T "CIT-RCR" """+ip+"""

"""
	try:
		print "Creating " + filename + "..."
		if not os.path.exists(directory):
			os.makedirs(directory)
		rdp_file = open(os.path.join(directory,filename), "w+")
		rdp_file.write(rdp_file_string)
		rdp_file.close()
		print "Complete"
	except Exception as e:
		print "ERROR creating RDP File:", e

if len(sys.argv) < 2:
    print "Usage: python workshop-rdp.py <input filename>"
    exit()
print "workshop-rdp.py: Creating RDP Files"
inputFilename = sys.argv[1]
inputFileBasename = os.path.splitext(os.path.basename(inputFilename))[0]

if not os.path.exists(WORKSHOP_RDP_LOCATION):
    os.makedirs(WORKSHOP_RDP_LOCATION)

tree = ET.parse(inputFilename)
root = tree.getroot()

pathToVirtualBox = root.find('vbox-setup').find('path-to-vboxmanage').text
netConfig = root.find('testbed-setup').find('network-config')
vmset = root.find('testbed-setup').find('vm-set')

# ---get ip address information
ipAddress = netConfig.find('ip-address').text

# ---here we look at each vmset
numClones = int(vmset.find('num-clones').text)
cloneSnapshots = vmset.find('clone-snapshots').text
linkedClones = vmset.find('linked-clones').text
baseGroupname = vmset.find('base-groupname').text

baseOutname = vmset.find('base-outname').text

vrdpBaseport = vmset.find('vrdp-baseport').text


for vm in vmset.findall('vm'):
    myBaseOutname = baseOutname
    for i in range(1, numClones + 1):
        vmname = vm.find('name').text

        # check to make sure the vm exists:
        getVMsCmd = [pathToVirtualBox, "list", "vms"]
        vmList = subprocess.check_output(getVMsCmd)
        if vmname not in vmList:
            print "VM not found: ", vmname
            print "Exiting"
            exit()

        # The new vm name ending with myBaseOutname
        newvmName = vmname + myBaseOutname + str(i)

		# The group name
        newGroupname = baseGroupname + "/Unit" + str(i)

        # vrdp setup
        vrdpEnabled = vm.find('vrdp-enabled').text
        if vrdpEnabled and vrdpEnabled == 'true':
            newVRDPname = str(vrdpBaseport)
            create_rdp_file(WORKSHOP_RDP_LOCATION+baseGroupname+"/",newvmName+"_"+str(vrdpBaseport)+".rdp", ipAddress, vrdpBaseport)
            create_rdesktop_file(WORKSHOP_RDP_LOCATION+baseGroupname+"/",newvmName+"_"+str(vrdpBaseport)+".sh", ipAddress, vrdpBaseport)
            vrdpBaseport = str(int(vrdpBaseport) + 1)
print """
**************************************************************************************
RDP File Creation Complete
**************************************************************************************
"""
