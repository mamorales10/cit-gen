import os
import re
import shlex
import xml.etree.ElementTree as ET
from subprocess import check_output, Popen, PIPE
from src.gui_constants import VBOXMANAGE_DIRECTORY, WORKSHOP_CONFIG_DIRECTORY, POSIX
import logging

def getVMs():
    getVMsCmd = [VBOXMANAGE_DIRECTORY, "list", "vms"]
    vmList = check_output(getVMsCmd)
    vmList = re.findall("\"(.*)\"", vmList)
    return list(vmList)


def getCloneNames(workshopName):
    names = []
    inputFilename = os.path.join(WORKSHOP_CONFIG_DIRECTORY, workshopName + ".xml")
    tree = ET.parse(inputFilename)
    root = tree.getroot()

    vmset = root.find('testbed-setup').find('vm-set')
    numClones = int(vmset.find('num-clones').text)
    baseOutname = vmset.find('base-outname').text

    for vm in vmset.findall('vm'):
        myBaseOutname = baseOutname
        for i in range(1, numClones + 1):
            vmname = vm.find('name').text
            newvmName = vmname + myBaseOutname + str(i)
            names.append(newvmName)
    return list(names)


def isRunning(workshopName):
    logging.debug("isRunning(): " + str(workshopName))
    clone_names = getCloneNames(workshopName)
    logging.debug("isRunning(): clone_names: " + str(clone_names))
    for clone_name in clone_names:
        cmd1 = VBOXMANAGE_DIRECTORY + " showvminfo " + "\"" + clone_name + "\""
        cmd2 = "grep -c \"running (since\""
        logging.debug("isRunning(): cmd1: " + str(cmd1))
        if POSIX:
            p1 = Popen(shlex.split(cmd1), shell=False, stdout=PIPE)
            p2 = Popen(shlex.split(cmd2), shell=False, stdin=p1.stdout, stdout=PIPE)
            output = int(p2.communicate()[0])
            if output == 0:
               return False
        else:
            return False
    return True


def hasClonesCreated(workshopName):
    vms = getVMs()
    clone_names = getCloneNames(workshopName)
    return set(clone_names) <= set(vms)


def getStatus(workshopName):
    # Check if clones are created
    if not hasClonesCreated(workshopName):
        return "Clones Not Created"
    # Clones are created. Check if running
    if isRunning(workshopName):
        return "Running"
    # Workshop is not running
    return "Ready"
