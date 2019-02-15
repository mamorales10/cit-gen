import time
import ast
import threading
import gi; gi.require_version('Gtk', '3.0')
from vboxmanage_utils import getCloneNames
from src.gui_constants import MANAGER_BIN_DIRECTORY, PADDING
from subprocess import Popen, PIPE
from gi.repository import Gtk


class WorkshopListBoxRow(Gtk.ListBoxRow):

    def __init__(self, workshop):
        super(Gtk.ListBoxRow, self).__init__()
        self.workshopName = workshop[0]
        self.num_available = workshop[1]
        self.add(Gtk.Label(str(self.workshopName) +
                           "\t\t\t\t\t\t\t\tUnits Available: " +
                           str(self.num_available) + "/" +
                           str(len(getCloneNames(self.workshopName)))))


class ManagerBox(Gtk.Box):

    def __init__(self):
        super(ManagerBox, self).__init__()
        self.num_clients = 0
        self.workshops_running = []
        self.p = None

        self.set_border_width(PADDING)
        self.outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=50)

        self.top_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.bottom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.outer_box.add(self.top_box)
        self.outer_box.add(self.bottom_box)

        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.top_box.pack_start(list_box, True, True, 0)

        manager_row = Gtk.ListBoxRow()
        manager_selection = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        manager_label = Gtk.Label("Manager", xalign=0)
        manager_selection.pack_start(manager_label, True, True, 0)
        switch = Gtk.Switch()
        switch.connect("notify::active", self.startManagerActionEvent)
        switch.set_active(False)
        switch.set_halign(Gtk.Align.END)
        manager_selection.pack_end(switch, True, True, 0)
        manager_row.add(manager_selection)
        list_box.add(manager_row)

        clients_row = Gtk.ListBoxRow()
        client_info = Gtk.Box()
        self.num_clients_label_header = Gtk.Label("Participants viewing frontend: ", xalign=0)
        self.num_clients_label_footer = Gtk.Label()
        client_info.pack_start(self.num_clients_label_header, True, True, 0)
        client_info.pack_start(self.num_clients_label_footer, True, True, 0)
        clients_row.add(client_info)
        list_box.add(clients_row)

        workshops_row = Gtk.ListBoxRow()
        workshops_running = Gtk.Box()
        self.workshops_running_label = Gtk.Label("Workshops Running:", xalign=0)
        self.workshops_running_label.set_halign(Gtk.Align.CENTER)
        workshops_running.pack_start(self.workshops_running_label, True, True, 0)
        workshops_row.add(workshops_running)
        self.bottom_box.pack_start(workshops_row, True, True, 0)
        self.bottom_box.show_all()

        self.workshops_list_box = Gtk.ListBox()
        self.workshops_list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.bottom_box.pack_start(self.workshops_list_box, True, True, 0)
        self.pack_start(self.outer_box, True, True, 0)

    def startManagerActionEvent(self, button, active):
        command = ["python", MANAGER_BIN_DIRECTORY+"/instantiator.py"]
        if button.get_active():
            # Start the thread that executes the process and filters its output
            t = threading.Thread(target=self.watchProcess, args=(command,))
            t.start()
        else:
            # Destroy the process and disable switch until process is terminated
            button.set_sensitive(False)
            self.destroy_process()

            # Check if process is still running and wait till finished to re-enable the switch
            while self.p.poll() is None:
                time.sleep(0.1)
            button.set_sensitive(True)

    def watchProcess(self, processPath):
        #Function for starting the process and capturing its stdout
        try:
            self.p = Popen(processPath, shell=False, stdout=PIPE, bufsize=1, cwd=MANAGER_BIN_DIRECTORY)
            with self.p.stdout:
                for line in iter(self.p.stdout.readline, b''):
                    if line.rstrip().lstrip() != "":
                        line = line.split(':')
                        if line[0] == "Participants viewing frontend":
                            self.num_clients = line[1]
                            self.num_clients_label_footer.set_label(str(self.num_clients))

                        elif line[0] == "Workshops available":
                            curr_workshops = ast.literal_eval(line[1])
                            if self.workshops_running != curr_workshops:
                                self.workshops_running = curr_workshops
                                self.manage_workshops_list(self.workshops_running)

            # wait for the subprocess to exit
            self.p.wait()
        except Exception as x:
            if self.p != None and self.p.poll() == None:
                self.p.terminate()

    def destroy_process(self):
        #Sharing thread memory, so we have access to the process that it creates and watches
        #if the process is still running, terminate it
        if self.p != None and self.p.poll() == None:
            self.p.terminate()

        # Restore labels and internal list of running workshops
        self.num_clients_label_footer.set_label("")
        self.workshops_running = None
        for child in self.workshops_list_box.get_children():
            self.workshops_list_box.remove(child)

    def manage_workshops_list(self, workshops):
        for workshop in workshops:
            if not self.workshop_is_displayed(workshop):
                self.workshops_list_box.add(WorkshopListBoxRow(workshop))
            else:
                for child in self.workshops_list_box.get_children():
                    if (child.workshopName == workshop[0]) and (child.num_available != workshop[1]):
                        child.num_available = workshop[1]
                        for label in child.get_children():
                            child.remove(label)
                        child.add(Gtk.Label(str(child.workshopName) +
                                            "\t\t\t\t\t\t\t\tUnits Available: " +
                                            str(child.num_available) + "/" +
                                            str(len(getCloneNames(child.workshopName)))))
        self.workshops_list_box.show_all()

    def workshop_is_displayed(self, workshop):
        for child in self.workshops_list_box.get_children():
            if child.workshopName == workshop[0]:
                return True
        return False
