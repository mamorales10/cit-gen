import os
import xml.etree.ElementTree as ET
import logging
from src.model.Material import Material
from src.model.VM import VM
from src.gui_constants import WORKSHOP_CONFIG_DIRECTORY, VBOXMANAGE_DIRECTORY


class Workshop:

    def __init__(self, workshopName, vmName):
        logging.debug("Created VM" + str(workshopName) + " " + str(vmName))
        self.filename = workshopName

        # These fields are workshop specific
        self.pathToVBoxManage = VBOXMANAGE_DIRECTORY # String
        self.ipAddress = "127.0.0.1" # String
        self.baseGroupName = workshopName # String
        self.numOfClones = "3" # Int
        self.cloneSnapshots = "true" # Bool
        self.linkedClones = "true" # Bool
        self.baseOutName = "101" # String
        self.vrdpBaseport = "1011" # int

        self.vmList = [] # VM
        if vmName!=None:
          # This will contain a list of VM objects
          vm=VM(vmName)
          self.vmList.append(vm)

        self.materialList = []

    def addVM(self, vmName):
        logging.debug("addVM() initiated " + str(vmName))
        self.vmList.append(VM(vmName))

    def addMaterial(self, materialAddress, materialName):
        logging.debug("addMaterial() initiated " + str(materialAddress) + " " + materialName)
        self.materialList.append(Material(materialAddress, materialName))

    def loadFileConfig(self, inputFile):
        logging.debug("loadFileConfig() initiated " + str(inputFile))
        self.filename = os.path.splitext(inputFile)[0]

        tree = ET.parse(os.path.join(WORKSHOP_CONFIG_DIRECTORY, inputFile))
        root = tree.getroot()

        self.pathToVBoxManage = root.find('vbox-setup').find('path-to-vboxmanage').text

        vmset = root.find('testbed-setup').find('network-config')
        self.ipAddress = vmset.find('ip-address').text

        vmset = root.find('testbed-setup').find('vm-set')
        self.baseGroupName = vmset.find('base-groupname').text
        self.numOfClones = vmset.find('num-clones').text
        self.cloneSnapshots = vmset.find('clone-snapshots').text
        self.linkedClones = vmset.find('linked-clones').text
        self.baseOutName = vmset.find('base-outname').text
        self.vrdpBaseport = vmset.find('vrdp-baseport').text

        for vm in vmset.findall('vm'):
            currentVM = VM(vm.find('name').text)
            currentVM.vrdpEnabled = vm.find('vrdp-enabled').text
            internalnetList = vm.findall('internalnet-basename')
            currentVM.internalnetBasenameList=[]
            for internalnet in internalnetList:
                currentVM.internalnetBasenameList.append(internalnet.text)
            self.vmList.append(currentVM)

        for material in vmset.findall('material'):
            currentMaterial = Material('', material.find('name').text)
            self.materialList.append(currentMaterial)
