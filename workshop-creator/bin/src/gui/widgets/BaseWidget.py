import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.gui_constants import BOX_SPACING, PADDING


# This class is a container that contains the base GUI
class BaseWidget(Gtk.Box):

    def __init__(self):
        super(BaseWidget, self).__init__()
        logging.debug("Creating Base Widget")
        self.set_border_width(PADDING)

        # Declaration of boxes
        self.outerBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=100)
        self.outerVertBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=BOX_SPACING)
        self.buttonsHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.vBoxManageHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.ipAddressHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.baseGroupNameHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.numClonesHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.cloneSnapshotsHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.linkedClonesHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.baseOutnameHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.vrdpBaseportHorBox = Gtk.Box(spacing=BOX_SPACING)

        # Declaration of labels
        self.vBoxManageLabel =      Gtk.Label("Path To VBoxManager:")
        self.ipAddressLabel =       Gtk.Label("IP Address:             ")
        self.baseGroupNameLabel =   Gtk.Label("Base Group Name:   ")
        self.numClonesLabel =       Gtk.Label("Number of Clones:   ")
        self.cloneSnapshotsLabel =  Gtk.Label("Clone Snapshots:    ")
        self.linkedClonesLabel =    Gtk.Label("Linked Clones:        ")
        self.baseOutnameLabel =     Gtk.Label("Base Outname:       ")
        self.vrdpBaseportLabel =    Gtk.Label("VRDP Baseport:       ")

        # Declaration of entrys
        self.vBoxManageEntry = Gtk.Entry()
        self.ipAddressEntry = Gtk.Entry()
        self.baseGroupNameEntry = Gtk.Entry()
        self.baseGroupNameEntry.set_sensitive(False)
        self.set_can_focus(False)

        self.numClonesEntry = Gtk.SpinButton()
        self.numClonesEntry.set_range(1, 50)
        self.numClonesEntry.set_increments(1, 5)
        self.cloneSnapshotsEntry = Gtk.ComboBoxText()
        self.cloneSnapshotsEntry.insert_text(0, "true")
        self.cloneSnapshotsEntry.insert_text(1, "false")
        self.linkedClonesEntry = Gtk.ComboBoxText()
        self.linkedClonesEntry.insert_text(0, "true")
        self.linkedClonesEntry.insert_text(1, "false")
        self.baseOutnameEntry = Gtk.Entry()
        self.vrdpBaseportEntry = Gtk.Entry()

        self.chooseVBoxPathButton = Gtk.Button("...")

        self.saveButton = Gtk.Button(label="Save Changes")

        self.initializeContainers()
        self.initializeLabels()
        self.initializeEntrys()

        self.vBoxManageHorBox.pack_end(self.chooseVBoxPathButton, False, False, 0)

    def initializeContainers(self):
        #TODO: HERE: need to add to the "right" side
        #Need to make this into 2 boxes (maybe three) and then left
        #justify left, right justify right and grow all equally
        self.pack_start(self.outerBox, True, True, PADDING)
        self.outerBox.add(self.outerVertBox)
        self.outerVertBox.add(self.buttonsHorBox)
        self.outerVertBox.add(self.vBoxManageHorBox)
        self.outerVertBox.add(self.ipAddressHorBox)
        self.outerVertBox.add(self.baseGroupNameHorBox)
        self.outerVertBox.add(self.numClonesHorBox)
        self.outerVertBox.add(self.linkedClonesHorBox)
        self.outerVertBox.add(self.cloneSnapshotsHorBox)
        self.outerVertBox.add(self.baseOutnameHorBox)
        self.outerVertBox.add(self.vrdpBaseportHorBox)
        self.outerBox.pack_end(self.saveButton, False, False, PADDING)

    def initializeLabels(self):
        self.vBoxManageHorBox.pack_start(self.vBoxManageLabel, False, False, PADDING)
        self.ipAddressHorBox.pack_start(self.ipAddressLabel, False, False, PADDING)
        self.baseGroupNameHorBox.pack_start(self.baseGroupNameLabel, False, False, PADDING)
        self.numClonesHorBox.pack_start(self.numClonesLabel, False, False, PADDING)
        self.cloneSnapshotsHorBox.pack_start(self.cloneSnapshotsLabel, False, False, PADDING)
        self.linkedClonesHorBox.pack_start(self.linkedClonesLabel, False, False, PADDING)
        self.baseOutnameHorBox.pack_start(self.baseOutnameLabel, False, False, PADDING)
        self.vrdpBaseportHorBox.pack_start(self.vrdpBaseportLabel, False, False, PADDING)

    def initializeEntrys(self):
        self.vBoxManageHorBox.pack_end(self.vBoxManageEntry, True, True, PADDING)
        self.ipAddressHorBox.pack_end(self.ipAddressEntry, True, True, PADDING)
        self.baseGroupNameHorBox.pack_end(self.baseGroupNameEntry, True, True, PADDING)
        self.numClonesHorBox.pack_end(self.numClonesEntry, True, True, PADDING)
        self.cloneSnapshotsHorBox.pack_end(self.cloneSnapshotsEntry, True, True, PADDING)
        self.linkedClonesHorBox.pack_end(self.linkedClonesEntry, True, True, PADDING)
        self.baseOutnameHorBox.pack_end(self.baseOutnameEntry, True, True, PADDING)
        self.vrdpBaseportHorBox.pack_end(self.vrdpBaseportEntry, True, True, PADDING)
