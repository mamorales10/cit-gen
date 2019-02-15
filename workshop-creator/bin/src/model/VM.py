import logging


class VM:

    def __init__(self, vmName):
        logging.debug("Created VM" + str(vmName))
        # These fields are VM specific
        self.name = vmName  # String
        self.vrdpEnabled = "false"  # Bool

        # This will contain a list of basenames
        self.internalnetBasenameList = []  # String
        self.internalnetBasenameList.append("intnet")

    def addInet(self, inetName):
        logging.debug("addInet(): appending inetName to VM: " + self.name)
        self.internalBasenameList.append(inetName)
