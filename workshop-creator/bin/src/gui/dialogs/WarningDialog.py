import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def WarningDialog(self, message):
    logging.debug("Creating Warning Dialog")
    dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, message)
    dialog.run()
    dialog.destroy()
