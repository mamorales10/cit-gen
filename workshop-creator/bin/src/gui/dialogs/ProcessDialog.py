import threading
import logging
import shlex
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib
from subprocess import Popen, PIPE
from src.gui_constants import POSIX


class ProcessDialog(Gtk.Dialog):

    def __init__(self, processPath, capture="stdout", granularity="line"): #other parameters: stdout/stderr, char/line-based
        
        Gtk.Dialog.__init__(self, title="Process Output Console Dialog")
        logging.debug("ProcessDialog(): initiated")
        #self.set_transient_for(parent.get_toplevel())
        #Variables needed for obtaining and displaying process output
        self.p = None
        self.proc_complete = False
        if capture == "stderr":
            self.capture = "stderr"
        else:
            self.capture = "stdout"
        if granularity == "char":
            self.granularity = "char"
        else:
            self.granularity = "line"

        #Configuraiton for this Gtk.Window
        self.set_default_size(400, 180)
        self.set_resizable(True)
        self.connect("destroy", self.destroy_progress)
        self.set_title("Process Output Console")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(600, 180)
        self.set_border_width(8)
        #Create the VBox in case we want to add additional items later
        self.dialogBox = self.get_content_area()
        self.mvbox = Gtk.VBox(False, 5)
        self.mvbox.set_border_width(10)
        self.dialogBox.add(self.mvbox)
        #create the scrolled window
        self.scrolled_window =Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        #self.scrolled_window.set_usize(460, 100)
        self.mvbox.add(self.scrolled_window)
        self.text_view = Gtk.TextView()
        self.msg_i = 0
        self.text_buffer = self.text_view.get_buffer()
        self.scrolled_window.add_with_viewport(self.text_view)
        self.text_view.connect("size-allocate", self.autoscroll)
        #Show the window
        self.show_all()
        #Start the thread that executes the process and captures its output
        t = threading.Thread(target=self.watchProcess, args=(processPath,))
        t.start()

    def autoscroll(self, *args):
        #The actual scrolling method
        adj = self.scrolled_window.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def appendText(self, msg):
        i = self.text_buffer.get_end_iter()
        #logging.debug("appendText(): " + str(msg))
        self.text_buffer.insert(i, str(msg), -1)

    def hideDialog(self):
        logging.debug("hideDialog(): initiated")
        self.hide()

    def watchProcess(self, processPath):
        logging.debug("watchProcess(): initiated")
        #Function for starting the process and capturing its output
        try:
            GLib.idle_add(self.appendText, "Starting process: " + str(processPath) + "\r\n")
            if POSIX:
                if self.capture=="stdout":
                    self.p = Popen(shlex.split(processPath, posix=POSIX), shell=False, stdout=PIPE, stderr=None)
                else:
                    self.p = Popen(shlex.split(processPath, posix=POSIX), shell=False, stdout=None, stderr=PIPE)
            else:
                if self.capture=="stdout":
                    self.p = Popen(processPath, shell=False, stdout=PIPE, stderr=None)
                else:
                    self.p = Popen(processPath, shell=False, stdout=None, stderr=PIPE)
            #logging.debug("watchProcess(): finished call to popen, observing stdout...")
            while True:
                #logging.debug("watchProcess(): reading input")
                if self.granularity == "line":
                    if self.capture == "stdout":
                        out = self.p.stdout.readline()
                    else:
                        out = self.p.stderr.readline()
                else:
                    if self.capture == "stdout":
                        out = self.p.stdout.read(1)
                    else:
                        out = self.p.stderr.read(1)
                if out == '' and self.p.poll() != None:
                    #logging.debug("watchProcess(): breaking out")
                    break
                else: 
                    #logging.debug("watchProcess(): calling idle_add")
                    GLib.idle_add(self.appendText, out)

            # wait for the subprocess to exit
            self.p.wait()
            self.proc_complete = True
            GLib.idle_add(self.hideDialog)
        except Exception as x:
            logging.error("watchProcess(): Something went wrong while running process: " + str(processPath) + "\r\n" + str(x))
            if self.p != None and self.p.poll() == None:
                self.p.terminate()
            GLib.idle_add(self.hideDialog)

    def destroy_progress(self, widget, data=None):
        logging.debug("destroy_progress(): initiated")
        #Sharing thread memory, so we have access to the process that it creates and watches
        #if the process is still running, terminate it
        if self.p != None and self.p.poll() == None:
            self.p.terminate()
        GLib.idle_add(self.hideDialog)

#if __name__ == "__main__":
     #a = ProcessWindow("ping localhost -t")
     #a = ProcessDialog("tracert -d www.google.com")
     #Gtk.main()
