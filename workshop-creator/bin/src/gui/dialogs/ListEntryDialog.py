import subprocess
import re
import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.gui.widgets.VMTreeWidget import VMTreeWidget
from src.gui_constants import BOX_SPACING, PADDING, VBOXMANAGE_DIRECTORY


class ListEntryDialog(Gtk.Dialog):

    def __init__(self, parent, message):
        logging.debug("Creating ListEntryDialog")
        Gtk.Dialog.__init__(self, "Add an item", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(300, 300)
        # This is the outer box, we need another box inside for formatting
        self.dialogBox = self.get_content_area()
        self.outerVertBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)
        self.dialogBox.add(self.outerVertBox)

        self.label = Gtk.Label(message)

        # Here we will place the tree view
        self.treeWidget = VMTreeWidget()

        self.entry = Gtk.Entry()
        self.entryText = None

        self.outerVertBox.pack_start(self.label, True, True, PADDING)
        self.outerVertBox.pack_start(self.treeWidget, True, True, PADDING)
        self.outerVertBox.pack_start(self.entry, True, True, PADDING)

        self.connect("response", self.dialogResponseActionEvent)
        self.show_all()
        self.status = None

        self.treeWidget.populateTreeStore(self.retrieveVMList())
        select = self.treeWidget.treeView.get_selection()
        select.connect("changed", self.onItemSelected)

    def retrieveVMList(self):
        # If there are no VM's the list will be empty
        vmList = subprocess.check_output([VBOXMANAGE_DIRECTORY, "list", "vms"])
        vmList = re.findall("\"(.*)\"", vmList)
        return vmList

    def onItemSelected(self, selection):
        model, treeiter = selection.get_selected()

        if treeiter == None:
            return

        vmName = model[treeiter][0]
        self.entry.set_text(vmName)

    def dialogResponseActionEvent(self, dialog, responseID):
        # OK was clicked and there is text
        if responseID == Gtk.ResponseType.OK and not self.entry.get_text_length() < 1:
            self.entryText = self.entry.get_text()
            self.status = True

        # Ok was clicked and there is no text
        elif responseID == Gtk.ResponseType.OK and self.entry.get_text_length() < 1:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, "The entry must not be empty.")
            dialog.run()
            dialog.destroy()

        # The operation was canceled
        elif responseID == Gtk.ResponseType.CANCEL or responseID == Gtk.ResponseType.DELETE_EVENT:
            self.entryText = None
            self.status = True
