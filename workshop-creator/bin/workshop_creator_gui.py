import sys
import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk
from src.gui.AppWindow import AppWindow


# This class is the main application
class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        logging.debug("Creating Application")
        super(Application, self).__init__(*args, application_id="workshop.creator.gui",
                         flags=Gio.ApplicationFlags.FLAGS_NONE,
                         **kwargs)
        self.window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        Gtk.Application.do_activate(self)
        if not self.window:
            self.window = AppWindow(application=self, title="Workshop Creator GUI")
        self.window.present()
        self.window.show_all()

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting Program")
    app = Application()
    app.run(sys.argv)
