import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.gui.widgets.InternalnetBasenameWidget import InternalnetBasenameWidget
from src.gui_constants import BOX_SPACING, PADDING


# This class is a container that will hold the vm information
class VMWidget(Gtk.Box):

    def __init__(self):
        logging.debug("Creating VMWidget")
        super(VMWidget, self).__init__()

        self.set_border_width(PADDING)

        # Declaration of boxes
        self.outerBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=100)
        self.outerVertBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=BOX_SPACING)
        self.nameHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.vrdpEnabledHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.iNetVerBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=BOX_SPACING)
        self.inetBasenameWidgetList = []

        # Declaration of labels
        self.nameLabel = Gtk.Label("Name:")
        self.vrdpEnabledLabel = Gtk.Label("VRDP Enabled:")
        self.saveLabel = Gtk.Label("Save Changes")

        # Declaration of entrys
        self.nameEntry = Gtk.Entry()
        self.nameEntry.set_sensitive(False)
        self.vrdpEnabledEntry = Gtk.ComboBoxText()
        self.vrdpEnabledEntry.insert_text(0, "true")
        self.vrdpEnabledEntry.insert_text(1, "false")
        self.addInetButton = Gtk.Button.new_with_label("Add Internalnet Basename")

        self.saveButton = Gtk.Button(label="Save Changes")

        self.initializeContainers()
        self.initializeLabels()
        self.initializeEntrys()

    def initializeContainers(self):
        self.pack_start(self.outerBox, True, True, PADDING)
        self.outerBox.add(self.outerVertBox)
        self.outerVertBox.add(self.nameHorBox)
        self.outerVertBox.add(self.vrdpEnabledHorBox)
        self.outerVertBox.add(self.iNetVerBox)
        self.outerVertBox.add(self.addInetButton)
        self.outerBox.pack_end(self.saveButton, False, False, PADDING)


    def initializeLabels(self):
        self.nameHorBox.pack_start(self.nameLabel, False, False, PADDING)
        self.vrdpEnabledHorBox.pack_start(self.vrdpEnabledLabel, False, False, PADDING)

    def initializeEntrys(self):
        self.nameHorBox.pack_end(self.nameEntry, True, True, PADDING)
        self.vrdpEnabledHorBox.pack_end(self.vrdpEnabledEntry, True, True, PADDING)

    def loadInets(self, internalNetList):

        # Clear the box of widgets
        for widget in self.iNetVerBox.get_children():
            self.iNetVerBox.remove(widget)

        # Clear the list of widgets
        self.inetBasenameWidgetList = []

        self.sizeOfList=len(internalNetList)
        for internalNet in internalNetList:
            inetWidget = InternalnetBasenameWidget()
            inetWidget.entry.set_text(internalNet)

            self.inetBasenameWidgetList.append(inetWidget)
            self.iNetVerBox.pack_start(inetWidget, False, False, 0)

    def initializeSignals(self, eventHandler):
        for widget in self.inetBasenameWidgetList:
            widget.connect("button-press-event", eventHandler)

    def addInet(self):
        inet = InternalnetBasenameWidget()
        inet.entry.set_text("default_inet")
        self.inetBasenameWidgetList.append(inet)
        self.iNetVerBox.pack_start(inet, False, False, 0)
        return inet

    def removeInet(self, inetNumber):

        if len(self.inetBasenameWidgetList) > 1:
            self.iNetVerBox.remove(self.inetBasenameWidgetList[inetNumber])
            self.inetBasenameWidgetList.remove(self.inetBasenameWidgetList[inetNumber])
