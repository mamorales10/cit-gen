import os
import logging
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from src.model.Session import Session
from src.gui.dialogs.ProcessDialog import ProcessDialog
from src.gui.dialogs.WarningDialog import WarningDialog
from src.gui.widgets.WorkshopListWidget import WorkshopListWidget
from src.gui_constants import (VM_STARTER_FILE_PATH, VM_POWEROFF_FILE_PATH, VBOXMANAGE_DIRECTORY,
                               WORKSHOP_CONFIG_DIRECTORY, WORKSHOP_CREATOR_FILE_PATH, WORKSHOP_RESTORE_FILE_PATH)
from vboxmanage_utils import getStatus, getCloneNames


class SuperMenu(Gtk.Box):

    def __init__(self):
        super(SuperMenu, self).__init__()
        self.session = Session()
        self.workshopListWidget = WorkshopListWidget(self.session.workshopList)
        self.pack_start(self.workshopListWidget, True, True, 0)

        # Signal initialization
        # This will handle when the tree selection is changed
        select = self.workshopListWidget.treeView.get_selection()
        select.connect("changed", self.onItemSelected)

        # Here we will initialize signals for the tree view right clicked
        self.workshopListWidget.treeView.connect("button-press-event", self.treeViewActionEvent)
        self.focusedTreeIter = None

        self.cloneWorkshop = Gtk.MenuItem("Signal - Create Clones")
        self.cloneWorkshop.connect("activate", self.cloneWorkshopActionEvent)
        self.startVMs = Gtk.MenuItem("Signal - Start VMs (headless)")
        self.startVMs.connect("activate", self.startVMsActionEvent)
        self.poweroffVMs = Gtk.MenuItem("Signal - Power Off VMs")
        self.poweroffVMs.connect("activate", self.poweroffVMsActionEvent)
        self.restoreSnapshots = Gtk.MenuItem("Signal - Restore Snapshots")
        self.restoreSnapshots.connect("activate", self.restoreSnapshotsActionEvent)
        self.deleteClones = Gtk.MenuItem("Signal - Delete Clones")
        self.deleteClones.connect("activate", self.deleteClonesActionEvent)

        # Workshop context menu
        self.workshopMenu = Gtk.Menu()

        self.workshopMenu.append(self.cloneWorkshop)
        self.workshopMenu.append(self.startVMs)
        self.workshopMenu.append(self.poweroffVMs)
        self.workshopMenu.append(self.restoreSnapshots)
        self.workshopMenu.append(self.deleteClones)
        self.workshopMenu.append(Gtk.SeparatorMenuItem())

    def treeViewActionEvent(self, treeView, event):
        logging.debug("treeViewActionEvent() initiated: " + str(event))
        # Get the current treeview model
        model = self.workshopListWidget.treeStore

        if event.button == 3:
            logging.debug("event.button == 3 ")
            pathInfo = treeView.get_path_at_pos(event.x, event.y)

            if pathInfo is not None:
                path, column, xCoord, yCoord = pathInfo
                treeIter = model.get_iter(path)
                self.focusedTreeIter = treeIter
                workshopName = model[treeIter][0]
                for workshop in self.session.workshopList:
                    if workshopName == workshop.filename:
                        self.session.currentWorkshop = workshop
                        break

                if not model.iter_has_child(treeIter):
                    self.workshopMenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
                    self.workshopMenu.show_all()

    def cloneWorkshopActionEvent(self, menuItem):
        logging.debug("cloneWorkshopActionEvent() initiated: " + str(menuItem))
        if self.session.currentWorkshop is None:
            WarningDialog(Gtk.Window(), "You must select a workshop before you can run the workshop.")
            return
        elif getStatus(self.session.currentWorkshop.filename) != "Clones Not Created":
            WarningDialog(Gtk.Window(), "Clones are already created for this workshop.")
            return

        workshopName = self.session.currentWorkshop.filename
        command = "python -u \"" + WORKSHOP_CREATOR_FILE_PATH + "\" \"" + os.path.join(WORKSHOP_CONFIG_DIRECTORY,
                                                                                       workshopName + ".xml\"")
        logging.debug("cloneWorkshopActionEvent(): instantiating ProcessDialog with command: " + command)
        pd = ProcessDialog(command)
        logging.debug("cloneWorkshopActionEvent(): running ProcessDialog")
        pd.run()
        pd.destroy()
        logging.debug("cloneWorkshopActionEvent(): returned from ProcessDialog")
        self.session.overwriteAllToSaveDirectory()
        self.refreshActionEvent(self.session.workshopList)

    def startVMsActionEvent(self, menuItem):
        logging.debug("startVMsActionEventActionEvent() initiated: " + str(menuItem))
        if self.session.currentWorkshop is None:
            WarningDialog(Gtk.Window(), "You must select a workshop before you can run the workshop.")
            return

        elif getStatus(self.session.currentWorkshop.filename) == "Clones Not Created":
            WarningDialog(Gtk.Window(), "Clones are not yet created.")
            return

        elif getStatus(self.session.currentWorkshop.filename) == "Running":
            WarningDialog(Gtk.Window(), "Workshop is already running.")
            return

        workshopName = self.session.currentWorkshop.filename
        command = "python -u \"" + VM_STARTER_FILE_PATH + "\" \"" + os.path.join(WORKSHOP_CONFIG_DIRECTORY,
                                                                                 workshopName + ".xml\"")
        logging.debug("startVMsActionEvent(): instantiating ProcessDialog")
        pd = ProcessDialog(command)
        logging.debug("startVMsActionEvent(): running ProcessDialog")
        pd.run()
        pd.destroy()
        logging.debug("startVMsActionEvent(): returned from ProcessDialog")
        self.refreshActionEvent(self.session.workshopList)

    def restoreSnapshotsActionEvent(self, menuItem):
        logging.debug("restoreSnapshotsActionEvent() initiated")
        self.session.runScript(WORKSHOP_RESTORE_FILE_PATH)

    def poweroffVMsActionEvent(self, menuItem):
        logging.debug("poweroffVMsActionEvent() initiated: " + str(menuItem))
        if self.session.currentWorkshop is None:
            WarningDialog(self.window, "You must select a workshop before you can run the workshop.")
            return
        #TODO: will uncomment when we code a way to see if VM running in windows
        #elif getStatus(self.session.currentWorkshop.filename) != "Running":
        #    WarningDialog(Gtk.Window(),  "Workshop is not running")
        #    return

        workshopName = self.session.currentWorkshop.filename
        command = "python -u \"" + VM_POWEROFF_FILE_PATH + "\" \"" + os.path.join(WORKSHOP_CONFIG_DIRECTORY,
                                                                                  workshopName + ".xml\"")
        logging.debug("poweroffVMsActionEvent(): instantiating ProcessDialog")
        pd = ProcessDialog(command)
        logging.debug("poweroffVMsActionEvent(): running ProcessDialog")
        pd.run()
        pd.destroy()
        logging.debug("poweroffVMsActionEvent(): returned from ProcessDialog")
        self.refreshActionEvent(self.session.workshopList)

    def deleteClonesActionEvent(self, menuItem):
        logging.debug("deleteClonesActionEvent() initiated: " + str(menuItem))
        if self.session.currentWorkshop is None:
            WarningDialog(self.window, "You must select a workshop before you can delete clones.")
            return
        elif getStatus(self.session.currentWorkshop.filename) == "Clones Not Created":
            WarningDialog(Gtk.Window(), "Clones are not yet created for this workshop.")
            return
        elif getStatus(self.session.currentWorkshop.filename) == "Running":
            WarningDialog(self.window, "Workshop is currently running. Cannot delete running clones.")
        elif getStatus(self.session.currentWorkshop.filename) == "Ready":
            workshopName = self.session.currentWorkshop.filename
            clones = getCloneNames(workshopName)

            for clone in clones:
                logging.debug("deleteClonesActionEvent(): instantiating ProcessDialog")
                pd = ProcessDialog(VBOXMANAGE_DIRECTORY + " unregistervm " + clone.replace(" ", "\\ ") + " --delete")
                logging.debug("deleteClonesActionEvent(): running ProcessDialog")
                pd.run()
                pd.destroy()
                logging.debug("deleteClonesActionEvent(): returned from ProcessDialog")
            self.refreshActionEvent(self.session.workshopList)

    def onItemSelected(self, selection):
        logging.debug("Item was selected: " + str(selection.get_selected))
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            filename = model[treeiter][0]

            for workshop in self.session.workshopList:
                if filename == workshop.filename:
                    self.session.currentWorkshop = workshop
                    break

    def refreshActionEvent(self, workshopList):
        self.workshopListWidget.refreshTreeStore(workshopList)
