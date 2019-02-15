import subprocess
import shutil
import xml.etree.ElementTree as ET
import shlex
import sys

def printError(message):
    print "\r\n\r\n!!!!!!!!!!\r\nERROR:\r\n", message, "\r\n!!!!!!!!!!\r\n"
    print "Exiting..."
    exit()

if len(sys.argv) < 2:
    print "Usage: python workshop-start.py <input filename>"
    exit()

inputFilename = sys.argv[1]

tree = ET.parse(inputFilename)
root = tree.getroot()

pathToVirtualBox = root.find('vbox-setup').find('path-to-vboxmanage').text
vmset = root.find('testbed-setup').find('vm-set')

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
        newvmName = vmname + myBaseOutname + str(i)

        # check to make sure the vm exists:
        getVMsCmd = [pathToVirtualBox, "list", "vms"]
        vmList = subprocess.check_output(getVMsCmd)

        if newvmName  not in vmList:
            print "VM not found: ", newvmName
            continue

        try:
            startCmd = [pathToVirtualBox, "startvm", newvmName, "--type", "headless"]
            print("\Starting VM in headless mode: " + newvmName)
            print("\nexecuting: ")
            print(startCmd)
            result = subprocess.check_output(startCmd)
            print(result)
        except Exception:
            print "Could not start VM:", newvmName
