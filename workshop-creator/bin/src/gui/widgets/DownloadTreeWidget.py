import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.gui_constants import PADDING


class DownloadTreeWidget(Gtk.Grid):

    def __init__(self):
        logging.debug("Creating DownloadTreeWidget")
        super(DownloadTreeWidget, self).__init__()

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

    def populateTreeStore(self, optionList):
        for option in optionList:
            self.treeStore.append(None, [option])

    def drawTreeView(self):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Downloadable Workshops", renderer, text=0)
        self.treeView.append_column(column)

    def setLayout(self):
        self.scrollableTreeList.set_min_content_width(100)
        self.scrollableTreeList.set_min_content_height(100)
        self.scrollableTreeList.set_vexpand(True)
        self.attach(self.scrollableTreeList, 0, 0, 4, 10)
        self.scrollableTreeList.add(self.treeView)
