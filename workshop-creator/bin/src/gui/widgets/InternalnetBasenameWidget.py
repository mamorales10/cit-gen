import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.gui_constants import BOX_SPACING, PADDING, STATIC_DIRECTORY


# This class is the widget inside of vmWidget
class InternalnetBasenameWidget(Gtk.EventBox):

    def __init__(self):
        logging.debug("Creating InternalnetWidget")
        super(InternalnetBasenameWidget, self).__init__()

        self.outerHorBox = Gtk.Box(spacing=BOX_SPACING)

        self.label = Gtk.Label("Internalnet Basename:")
        self.entry = Gtk.Entry()
        self.removeInetButton = Gtk.Button()
        self.removeInetButton.set_image(Gtk.Image.new_from_file(STATIC_DIRECTORY + "/delete-icon.png"))
        self.removeInetButtonHandlerID = 0

        self.initialize()

    #TODO: is this needed?
    def initialize(self):
        self.add(self.outerHorBox)

        self.outerHorBox.pack_start(self.label, False, False, PADDING)
        self.outerHorBox.pack_end(self.removeInetButton, False, False, PADDING)
        self.outerHorBox.pack_end(self.entry, True, True, PADDING)
