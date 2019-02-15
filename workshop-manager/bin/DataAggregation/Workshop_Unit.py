class Workshop_Unit:
    """ A Workshop_Unit encapsulates Workshop Units.

    Attributes:
        workshopName (str): The name of the workshop.
        vms (list of str): A list of Virtual Box VMs that are used for a specific unit.
        rdp_files (list of str): A list of paths to rdp files that are used to connect to vms.
        rdesktop_files (list of str): A list of paths to rdesktop files that are used to connect ot vms.
    """

    def __init__(self, workshopName, vms, rdp_files, rdesktop_files):
        """ Constructor for a Workshop Unit object.

        Args:
            workshopName (str): The name of the workshop.
            materials (list of str): A list of names of Virtual Box VMs that are used for a specific unit.
            rdp_files (list of str): A list of paths to rdp files that are used to connect to vms.
            rdesktop_files (list of str): A list of paths to rdesktop files that are used to connect ot vms.
        """
        self.workshopName = workshopName
        self.vms = vms
        self.rdp_files = rdp_files
        self.rdesktop_files = rdesktop_files

    def __eq__(self, other):
        return (self.workshopName == other.workshopName) and (self.vms == other.vms) and (self.rdp_files == other.rdp_files) and (self.rdesktop_files == other.rdesktop_files)
