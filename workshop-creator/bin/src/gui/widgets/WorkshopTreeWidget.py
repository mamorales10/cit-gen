import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.gui_constants import MATERIAL_TREE_LABEL, VM_TREE_LABEL, PADDING


# This class is a widget that is a grid, it holds the structure of the tree view
class WorkshopTreeWidget(Gtk.Grid):

    def __init__(self):
        logging.debug("Creating WorkshopTreeWidget")
        super(WorkshopTreeWidget, self).__init__()

        self.set_border_width(PADDING)

        # Initialized fields
        self.treeStore = Gtk.TreeStore(str)
        self.treeView = Gtk.TreeView(self.treeStore)
        self.scrollableTreeList = Gtk.ScrolledWindow()
        self.initializeContainers()
        self.drawTreeView()
        self.setLayout()

    def initializeContainers(self):
        self.set_column_homogeneous(True)
        self.set_row_homogeneous(True)

    def populateTreeStore(self, workshopList):
        for workshop in workshopList:
            treeIter = self.treeStore.append(None, [workshop.filename])

            for vm in workshop.vmList:
                self.treeStore.append(treeIter, [VM_TREE_LABEL+vm.name])
            for material in workshop.materialList:
                self.treeStore.append(treeIter, [MATERIAL_TREE_LABEL+material.name])

    def clearTreeStore(self):
        self.treeStore.clear()

    def addNode(self, workshopName, vmName):
        treeIter = self.treeStore.append(None, [workshopName])
        self.treeStore.append(treeIter, [VM_TREE_LABEL+vmName])

    def addChildNode(self, workshopTreeIter, vmName):
        self.treeStore.append(workshopTreeIter, [vmName])

    def drawTreeView(self):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Workshops", renderer, text=0)
        self.treeView.append_column(column)

    def setLayout(self):
        self.scrollableTreeList.set_min_content_width(200)
        self.scrollableTreeList.set_vexpand(True)
        self.attach(self.scrollableTreeList, 0, 0, 4, 10)
        self.scrollableTreeList.add(self.treeView)
