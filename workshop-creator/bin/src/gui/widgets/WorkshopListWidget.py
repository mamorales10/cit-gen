import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.gui_constants import PADDING
from vboxmanage_utils import getStatus


# This class is a widget that is a grid, it holds the structure of the tree view
class WorkshopListWidget(Gtk.Grid):

    def __init__(self, workshopList):
        logging.debug("Creating WorkshopTreeWidget")
        super(WorkshopListWidget, self).__init__()

        self.set_border_width(PADDING)

        # Initialized fields
        self.workshopList = workshopList
        self.treeStore = Gtk.TreeStore(str, str)
        self.treeView = Gtk.TreeView(self.treeStore)
        self.scrollableTreeList = Gtk.ScrolledWindow()
        self.initializeContainers()
        self.drawTreeView()
        self.setLayout()
        self.populateTreeStore()

    def initializeContainers(self):
        self.set_column_homogeneous(True)
        self.set_row_homogeneous(True)

    def populateTreeStore(self):
        for workshop in self.workshopList:
            treeIter = self.treeStore.append(None, [workshop.filename, getStatus(workshop.filename)])

            # for vm in workshop.vmList:
            #     self.treeStore.append(treeIter, [VM_TREE_LABEL+vm.name])

    def clearTreeStore(self):
        self.treeStore.clear()

    def drawTreeView(self):
        name_column = Gtk.TreeViewColumn("Workshop")
        workshop_name = Gtk.CellRendererText()
        name_column.pack_start(workshop_name, True)
        name_column.add_attribute(workshop_name, "text", 0)
        self.treeView.append_column(name_column)

        status_column = Gtk.TreeViewColumn("Status")
        workshop_status = Gtk.CellRendererText()
        status_column.pack_start(workshop_status, True)
        status_column.add_attribute(workshop_status, "text", 1)
        self.treeView.append_column(status_column)

    def setLayout(self):
        self.scrollableTreeList.set_min_content_width(200)
        self.scrollableTreeList.set_vexpand(True)
        self.attach(self.scrollableTreeList, 0, 0, 4, 10)
        self.scrollableTreeList.add(self.treeView)

    def refreshTreeStore(self, workshopList):
        self.clearTreeStore()
        self.workshopList = workshopList
        self.populateTreeStore()
