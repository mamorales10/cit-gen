import logging


class Material:
    def __init__(self, materialAddress, materialName):
        logging.debug("Created Material" + str(materialAddress) + " " + materialName)
        self.address = materialAddress
        self.name = materialName
        #self.name = self.address.split('\\')
        #self.name = self.name[len(self.name)-1]
