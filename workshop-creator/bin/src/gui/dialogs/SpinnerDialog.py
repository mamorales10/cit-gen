import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.gui_constants import PADDING


class SpinnerDialog(Gtk.Dialog):

    def __init__(self, parent, message):
        logging.debug("Creating Spinner Dialog")
        Gtk.Dialog.__init__(self, "", parent, 0)

        self.set_deletable(False)
        self.dialogBox = self.get_content_area()
        self.set_resizable(False)
        self.set_default_size(400, 180)
        self.outerVerBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.label = Gtk.Label(message)
        self.spinner = Gtk.Spinner()
        self.dialogBox.add(self.outerVerBox)
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar_is_hidden = False
        self.outerVerBox.pack_start(self.label, True, True, PADDING)
        self.outerVerBox.pack_start(self.progress_bar, True, True, PADDING)
        self.outerVerBox.pack_start(self.spinner, True, True, PADDING)

        self.show_all()
        self.spinner.start()

    def setProgressVal(self, val):
        self.progress_bar.set_fraction(val)

    def setLabelVal(self, text):
        self.label.set_text(text)

    def setTitleVal(self, text):
        self.set_title(text)

    def hideProgressBar(self):
        if not self.progress_bar_is_hidden:
            self.progress_bar.hide()

    def showProgressBar(self):
        if self.progress_bar_is_hidden:
            self.progress_bar.show()
