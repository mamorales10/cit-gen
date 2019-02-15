import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class ExportImportProgressDialog(Gtk.Dialog):

    def __init__(self, parent, message, currentTotal, total):
        logging.debug("Creating ExportImportProgressDialog" )
        Gtk.Dialog.__init__(self, "Workshop Wizard", parent, 0)

        self.set_default_size(50, 75)
        self.set_deletable(False)

        self.currentTotal = currentTotal
        self.total = total

        # This is the outer box, we need another box inside for formatting
        self.dialogBox = self.get_content_area()
        self.outerVerBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)
        self.dialogBox.add(self.outerVerBox)

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_show_text(True)
        self.outerVerBox.pack_start(self.progressbar, True, True, PADDING)

        self.progressbar.set_text(message)

        self.timeout_id = GObject.timeout_add(1000, self.on_timeout, None)

        self.show_all()

    def on_timeout(self, user_data):

        new_value = self.currentTotal[0] / self.total

        if new_value >= 1:
            self.destroy()
            return False

        self.progressbar.set_fraction(new_value)

        # As this is a timeout function, return True so that it
        # continues to get called
        return True
