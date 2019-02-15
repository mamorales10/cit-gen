import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.gui_constants import BOX_SPACING, PADDING


# This class is a container that will hold the material information
class MaterialWidget(Gtk.Box):

    def __init__(self):
        logging.debug("Initializing Material Widget")
        super(MaterialWidget, self).__init__()

        self.set_border_width(PADDING)

        # Declaration of boxes
        self.outerVertBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=BOX_SPACING)
        self.addressHorBox = Gtk.Box(spacing=BOX_SPACING)
        self.nameHorBox = Gtk.Box(spacing=BOX_SPACING)

        # Declaration of labels
        self.nameLabel = Gtk.Label("Name:")
        # Declaration of entrys
        self.nameEntry = Gtk.Entry()
        self.nameEntry.set_sensitive(False)

        #initialize containers
        #self.add(self.outerVertBox)
        self.pack_start(self.outerVertBox, True, True, PADDING)
        self.outerVertBox.add(self.addressHorBox)
        self.outerVertBox.add(self.nameHorBox)

        #initialize labels
        self.nameHorBox.pack_start(self.nameLabel, False, False, PADDING)

        #initialize entries
        self.nameHorBox.pack_end(self.nameEntry, True, True, PADDING)
