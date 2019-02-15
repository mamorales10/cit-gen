import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class ProgressWindow(Gtk.Window):

    def __init__(self, title_text):
        Gtk.Window.__init__(self, title=title_text)
        #Configuraiton for this Gtk.Window
        self.set_default_size(250, 180)
        self.set_resizable(True)
        self.connect("destroy", self.destroy_progress)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(8)
        #Create the VBox in case we want to add additional items later
        self.vbox = Gtk.VBox(False, 5)
        self.vbox.set_border_width(10)
        self.add(self.vbox)
        #Create the scrolled window
        self.scrolled_window =Gtk.ScrolledWindow()
        self.vbox.add(self.scrolled_window)
        self.text_view = Gtk.TextView()
        self.msg_i = 0
        self.text_buffer = self.text_view.get_buffer()
        self.scrolled_window.add_with_viewport(self.text_view)
        self.text_view.connect("size-allocate", self.autoscroll)
        #A progress bar to show the status
        self.progress_bar = Gtk.ProgressBar()
        self.vbox.add(self.progress_bar)
        #Show the window
        self.show_all()

    def autoscroll(self, *args):
        #The actual scrolling method
        adj = self.scrolled_window.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def destroy_progress(self, widget, data=None):
        self.destroy()

    def appendText(self, text):
        i = self.text_buffer.get_end_iter()
        self.text_buffer.insert(i, str(text), -1)
            
    #public functions to change the window items
    def setProgressVal(self,val):
        self.progress_bar.set_fraction(val)
        
    def setTitleVal(self, text):
        self.set_title(text)
# if __name__ == "__main__":
#     #a = ProcessWindow("ping localhost -t")
#     a = ProcessWindow("tracert -d www.google.com")
#     Gtk.main()
