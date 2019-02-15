import os
import shutil
import logging
import xml.etree.ElementTree as ET
import urllib2
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
from src.gui.manager_gui import ManagerBox
from src.gui.super_menu import SuperMenu
from src.gui.dialogs.EntryDialog import EntryDialog
from src.gui.dialogs.ListEntryDialog import ListEntryDialog
from src.gui.dialogs.ProcessDialog import ProcessDialog
from src.gui.dialogs.SpinnerDialog import SpinnerDialog
from src.gui.dialogs.WarningDialog import WarningDialog
from src.gui.dialogs.DownloadDialog import DownloadDialog
from src.gui.widgets.BaseWidget import BaseWidget
from src.gui.widgets.WorkshopTreeWidget import WorkshopTreeWidget
from src.gui.widgets.MaterialWidget import MaterialWidget
from src.gui.widgets.VMWidget import VMWidget
from src.model.Session import Session
from src.gui_constants import (BOX_SPACING, PADDING, MATERIAL_TREE_LABEL, VM_TREE_LABEL,
                               WORKSHOP_RDP_CREATOR_FILE_PATH, WORKSHOP_MATERIAL_DIRECTORY,
                               WORKSHOP_CONFIG_DIRECTORY, WORKSHOP_CREATOR_FILE_PATH,
                               WORKSHOP_RESTORE_FILE_PATH, WORKSHOP_RDP_DIRECTORY,
                               VM_POWEROFF_FILE_PATH, VM_STARTER_FILE_PATH,
                               VBOXMANAGE_DIRECTORY,
                               ONLINE_INDEX_FILE, WORKSHOP_TMP_DIRECTORY)


# This class contains the main window, its main container is a notebook
class AppWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        logging.debug("Creating AppWindow")
        super(AppWindow, self).__init__(*args, **kwargs)
        self.set_default_size(250, 180)
        # self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(5)
        # TODO: fix error when soft saving
        self.isRemoveVM = False

        # Layout container initialization
        self.windowBox = Gtk.Box(spacing=BOX_SPACING)
        self.actionBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)
        self.actionEventBox = Gtk.EventBox()
        self.scrolledActionBox = Gtk.ScrolledWindow()
        self.scrolledInnerBox = Gtk.Box(spacing=BOX_SPACING, orientation=Gtk.Orientation.VERTICAL)

        self.managerBox = ManagerBox()
        self.superMenu = SuperMenu()

        self.notebook = Gtk.Notebook()
        self.notebook.append_page(self.windowBox, Gtk.Label("Configuration"))
        self.notebook.append_page(self.superMenu, Gtk.Label("VBox Actions"))
        self.notebook.append_page(self.managerBox, Gtk.Label("Frontend"))
        self.notebook.connect("switch_page", self.notebookChangeHandler)

        # Widget creation
        self.workshopTree = WorkshopTreeWidget()
        self.currentModel = None
        self.currentIter = None
        self.baseWidget = BaseWidget()
        self.vmWidget = VMWidget()
        self.materialWidget = MaterialWidget()
        self.downloadIndex = None

        # if the currently highlighted tree element is a parent, its a workshop
        self.isParent = None

        # Initialization
        self.initializeContainers()
        self.session = Session()
        self.workshopTree.populateTreeStore(self.session.workshopList)

        # Signal initialization
        # This will handle when the tree selection is changed
        select = self.workshopTree.treeView.get_selection()
        select.connect("changed", self.onItemSelected)

        # This is the signal for the file chooser under the vbox path
        self.baseWidget.chooseVBoxPathButton.connect("clicked", self.onVBoxPathClicked)

        # This will get called when the window terminates
        self.connect("delete-event", self.on_delete)

        self.vmWidget.addInetButton.connect("clicked", self.addInetEventHandler)
        self.vmWidget.saveButton.connect("clicked", self.saveButtonHandler)
        self.baseWidget.saveButton.connect("clicked", self.saveButtonHandler)

        # Currentwidget in focus
        self.focusedInetWidget = None

        # Here we will initialize signals for the tree view right clicked
        self.workshopTree.treeView.connect("button-press-event", self.treeViewActionEvent)
        self.focusedTreeIter = None

        # Here we will have all the menu items
        self.addWorkshop = Gtk.MenuItem("New Workshop")
        self.addWorkshop.connect("activate", self.addWorkshopActionEvent)
        self.importWorkshop = Gtk.MenuItem("Import Workshop from EBX archive")
        self.importWorkshop.connect("activate", self.importActionEvent)
        self.downloadFromRepo = Gtk.MenuItem("Download Workshop From Repo")
        self.downloadFromRepo.connect("activate", self.download)

        self.createRDP = Gtk.MenuItem("Create RDP Files")
        self.createRDP.connect("activate", self.createRDPActionEvent)

        self.removeWorkshop = Gtk.MenuItem("Remove Workshop")
        self.removeWorkshop.connect("activate", self.removeWorkshopActionEvent)
        self.exportWorkshop = Gtk.MenuItem("Export Workshop")
        self.exportWorkshop.connect("activate", self.exportWorkshopActionEvent)
        self.addVM = Gtk.MenuItem("Add VM")
        self.addVM.connect("activate", self.addVMActionEvent)
        self.addMaterial = Gtk.MenuItem("Add Material File")
        self.addMaterial.connect("activate", self.addMaterialActionEvent)

        self.removeItem = Gtk.MenuItem("Remove Workshop Item")
        self.removeItem.connect("activate", self.removeVMActionEvent)

        # Workshop context menu
        self.workshopMenu = Gtk.Menu()
        self.workshopMenu.append(self.addVM)
        self.workshopMenu.append(self.addMaterial)
        self.workshopMenu.append(Gtk.SeparatorMenuItem())

        self.workshopMenu.append(self.createRDP)
        self.workshopMenu.append(Gtk.SeparatorMenuItem())

        self.workshopMenu.append(self.removeWorkshop)
        self.workshopMenu.append(self.exportWorkshop)

        # context menu for blank space
        self.blankMenu = Gtk.Menu()
        self.blankMenu.append(self.addWorkshop)
        self.blankMenu.append(self.importWorkshop)
        self.blankMenu.append(self.downloadFromRepo)

        # VM context menu
        self.itemMenu = Gtk.Menu()
        self.itemMenu.append(self.removeItem)

        # Capture Ctrl-S for saving
        self.connect("key-press-event", self.keyHandler)

    def notebookChangeHandler(self, page, page_num, user_data):
        logging.debug("notebookChangeHandler(): Notebook changed " + "page: " + str(page.get_tab_label_text(page_num)))
        #Need to set the current workshop to whatever is highlighted - that way when save, we save to the correct one!
        selection = self.workshopTree.treeView.get_selection()
        model, treeiter = selection.get_selected()
        self.currentModel = model
        self.currentIter = treeiter

        if treeiter == None:
            return

        if model.iter_has_child(treeiter):
            self.isParent = True
            filename = model[treeiter][0]
            self.session.currentWorkshop = None
            matchFound = False

            for workshop in self.session.workshopList:
                if filename == workshop.filename:
                    self.session.currentWorkshop = workshop
                    matchFound = True
                    break

            if not matchFound:
                return
            logging.debug("onItemSelected(): working with matching workshop name: " + filename)

        elif not model.iter_has_child(treeiter):
            self.isParent = False
            vmName = model[treeiter][0]
            treeiter = model.iter_parent(treeiter)
            filename = model[treeiter][0]
            self.session.currentWorkshop = None
            matchFound = False

            for workshop in self.session.workshopList:
                if filename == workshop.filename:
                    self.session.currentWorkshop = workshop
                    matchFound = True
                    break

            if not matchFound:
                return

    def saveButtonHandler(self, widget):
        logging.debug("saveButtonHandler(): initiated")
        model, treeIter = self.workshopTree.treeView.get_selection().get_selected()
        logging.debug("saveButtonHandler(): selected tree items is: " + str(model[treeIter][0]))

        self.softSave()
        self.hardSave()

    def keyHandler(self, widget, event):
        # Check if Ctrl is held down while pressing the 's' or 'S' key. 'S' will occur if caps-lock is on
        if event.state == Gdk.ModifierType.CONTROL_MASK and event.keyval == Gdk.KEY_s or \
                event.state == Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.LOCK_MASK and event.keyval == Gdk.KEY_S:
            self.softSave()
            self.hardSave()

    def initializeContainers(self):
        logging.debug("initializeContainers(): initiated")
        self.add(self.notebook)

        self.windowBox.pack_start(self.workshopTree, True, True, PADDING)
        self.windowBox.pack_end(self.actionEventBox, True, True, PADDING)

        self.actionEventBox.add(self.actionBox)
        self.actionBox.pack_start(self.scrolledActionBox, True, True, PADDING)

        self.scrolledActionBox.add(self.scrolledInnerBox)
        self.scrolledActionBox.set_min_content_width(450)
        self.scrolledActionBox.set_min_content_height(600)

    def onItemSelected(self, selection):
        logging.debug("Item was selected: " + str(selection))
        #save any changes that may have occured when working with the previous selection (workshop)
        self.softSave()
        self.hardSave()

        model, treeiter = selection.get_selected()
        self.currentModel = model
        self.currentIter = treeiter

        if treeiter == None:
            return

        if model.iter_has_child(treeiter):
            self.isParent = True
            filename = model[treeiter][0]
            self.session.currentWorkshop = None
            matchFound = False

            for workshop in self.session.workshopList:
                if filename == workshop.filename:
                    self.session.currentWorkshop = workshop
                    matchFound = True
                    break

            if not matchFound:
                return
            logging.debug("onItemSelected(): working with matching workshop name: " + filename)

            # The clicked row in the tree was valid so we will need to
            # clear all children in the main container and add the new one
            for widget in self.scrolledInnerBox.get_children():
                self.scrolledInnerBox.remove(widget)

            self.scrolledInnerBox.pack_start(self.baseWidget, True, True, PADDING)

            self.baseWidget.vBoxManageEntry.set_text(self.session.currentWorkshop.pathToVBoxManage)
            self.baseWidget.ipAddressEntry.set_text(self.session.currentWorkshop.ipAddress)
            self.baseWidget.baseGroupNameEntry.set_text(self.session.currentWorkshop.baseGroupName)
            self.baseWidget.numClonesEntry.set_value(int(float(self.session.currentWorkshop.numOfClones)))
            # self.baseWidget.cloneSnapshotsEntry.set_text(self.session.currentWorkshop.cloneSnapshots)
            self.holdClone = 0
            if self.session.currentWorkshop.cloneSnapshots == "false":
                self.holdClone = 1
            self.baseWidget.cloneSnapshotsEntry.set_active(self.holdClone)
            # self.baseWidget.linkedClonesEntry.set_text(self.session.currentWorkshop.linkedClones)
            self.holdClone = 0
            if self.session.currentWorkshop.linkedClones == "false":
                self.holdClone = 1
            self.baseWidget.linkedClonesEntry.set_active(self.holdClone)
            self.baseWidget.baseOutnameEntry.set_text(self.session.currentWorkshop.baseOutName)
            self.baseWidget.vrdpBaseportEntry.set_text(self.session.currentWorkshop.vrdpBaseport)

            self.actionBox.show_all()

        elif not model.iter_has_child(treeiter):
            self.isParent = False
            vmName = model[treeiter][0]
            treeiter = model.iter_parent(treeiter)
            filename = model[treeiter][0]
            self.session.currentWorkshop = None
            matchFound = False

            for workshop in self.session.workshopList:
                if filename == workshop.filename:
                    self.session.currentWorkshop = workshop
                    matchFound = True
                    break

            if not matchFound:
                return

            self.currentVM = None
            self.currentMaterial = None
            self.session.currentVM = None
            self.session.currentMaterial = None
            matchFound = False
            for vmWidget in self.session.currentWorkshop.vmList:
                if vmName == VM_TREE_LABEL + vmWidget.name:
                    self.session.currentVM = vmWidget
                    matchFound = True
                    break

            if not matchFound:
                for materialWidget in self.session.currentWorkshop.materialList:
                    if vmName == MATERIAL_TREE_LABEL + materialWidget.name:
                        self.session.currentMaterial = materialWidget
                        matchFound = True
                        break

            if not matchFound:
                return

            for widget in self.scrolledInnerBox.get_children():
                self.scrolledInnerBox.remove(widget)

            if self.session.currentVM != None:
                self.scrolledInnerBox.pack_start(self.vmWidget, True, True, PADDING)

                self.vmWidget.nameEntry.set_text(self.session.currentVM.name)
                self.holdVRDP = 0
                if self.session.currentVM.vrdpEnabled == "false":
                    self.holdVRDP = 1
                self.vmWidget.vrdpEnabledEntry.set_active(self.holdVRDP)
                self.vmWidget.loadInets(self.session.currentVM.internalnetBasenameList)

                if len(self.vmWidget.inetBasenameWidgetList) > 0:
                    for k, rientry in enumerate(self.vmWidget.inetBasenameWidgetList):
                        rientry.removeInetButtonHandlerID = \
                            rientry.removeInetButton.connect("clicked", self.removeInetEventHandler, k)

            elif self.session.currentMaterial != None:
                self.scrolledInnerBox.pack_start(self.materialWidget, True, True, PADDING)

                self.materialWidget.nameEntry.set_text(self.session.currentMaterial.name)
            self.actionBox.show_all()

        self.softSave()
        self.hardSave()


    # This handles clicking the vboxpath
    def onVBoxPathClicked(self, button):
        logging.debug("VBox Path Clicked " + str(button))
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
                                       Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        dialog.set_filename(self.baseWidget.vBoxManageEntry.get_text())
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.baseWidget.vBoxManageEntry.set_text(dialog.get_filename())
        # elif response == Gtk.ResponseType.CANCEL:
        dialog.destroy()

    # Will save all changes to ram
    def softSave(self):
        logging.debug("Soft Saving")
        if self.isParent == True:
            self.holdSnaps = "true"
            if self.baseWidget.cloneSnapshotsEntry.get_active_text() == "false":
                self.holdSnaps = "false"
            self.holdLinked = "true"
            if self.baseWidget.linkedClonesEntry.get_active_text() == "false":
                self.holdLinked = "false"
            #TODO: here be the dragons!
            logging.debug("softSave(): baseWidget group name: " + self.baseWidget.baseGroupNameEntry.get_text())
            self.session.softSaveWorkshop(self.baseWidget.vBoxManageEntry.get_text(),
                                          self.baseWidget.ipAddressEntry.get_text(),
                                          self.baseWidget.baseGroupNameEntry.get_text(),
                                          str(self.baseWidget.numClonesEntry.get_value_as_int()), self.holdSnaps,
                                          self.holdLinked, self.baseWidget.baseOutnameEntry.get_text(),
                                          self.baseWidget.vrdpBaseportEntry.get_text())

        elif self.isParent == False:

            if self.session.currentVM != None:
                if not self.isRemoveVM:
                    self.currentModel.set(self.currentIter, 0, VM_TREE_LABEL + self.vmWidget.nameEntry.get_text())
                self.holdInternalnetBasenameList = []
                for inetWidget in self.vmWidget.inetBasenameWidgetList:
                    self.holdInternalnetBasenameList.append(inetWidget.entry.get_text())

                self.holdVRDP = "true"
                if self.vmWidget.vrdpEnabledEntry.get_active_text() == "false":
                    self.holdVRDP = "false"
                self.session.softSaveVM(self.vmWidget.nameEntry.get_text(), self.holdVRDP,
                                        self.holdInternalnetBasenameList)
            elif self.session.currentMaterial != None:
                if not self.isRemoveVM:
                    self.currentModel.set(self.currentIter, 0,
                                          MATERIAL_TREE_LABEL + self.materialWidget.nameEntry.get_text())
                self.session.softSaveMaterial(self.materialWidget.nameEntry.get_text())
            self.isRemoveVM = False

    # Will save all changed to the disk
    def hardSave(self):
        logging.debug("Hard Saving")
        self.session.hardSave()

    # Performs a softsave then a hardsave
    def fullSave(self):
        logging.debug("Full Saving")
        self.softSave()
        self.hardSave()
        self.superMenu.refreshActionEvent(self.session.workshopList)

    def createRDPActionEvent(self, menuItem):
        logging.debug("createRDPActionEvent() initiated: " + str(menuItem))
        logging.debug("running workshop rdp creation script")
        self.session.runScript(WORKSHOP_RDP_CREATOR_FILE_PATH)
        logging.debug("copying rdp files to manager directory")
        self.session.overwriteRDPToManagerSaveDirectory()

    def addInetEventHandler(self, menuItem):
        logging.debug("addInetEventHandler() initiated: " + str(menuItem))
        inet = self.vmWidget.addInet()
        inet.removeInetButtonHandlerID = inet.removeInetButton.connect("clicked",
                                                                       self.removeInetEventHandler,
                                                                       len(self.vmWidget.inetBasenameWidgetList) - 1)
        self.actionBox.show_all()

    def removeInetEventHandler(self, menuItem, *data):
        logging.debug("removeInetEventHandler() initiated: " + str(menuItem) + " " + str(data))

        if len(self.vmWidget.inetBasenameWidgetList) > 1:
            self.vmWidget.removeInet(data[0])

            # Adjust button handlers for remaining inets
            i = data[0]
            for inet in self.vmWidget.inetBasenameWidgetList[i:]:
                inet.removeInetButton.handler_disconnect(inet.removeInetButtonHandlerID)
                inet.removeInetButtonHandlerID = inet.removeInetButton.connect("clicked", self.removeInetEventHandler, i)
                i += 1
            self.actionBox.show_all()

        else:
            WarningDialog(self, "There must be at least one Internalnet Basename.")
            return

    def treeViewActionEvent(self, treeView, event):
        logging.debug("treeViewActionEvent() initiated: " + str(event))
        # Get the current treeview model
        model = self.workshopTree.treeStore

        if event.button == 3:
            logging.debug("event.button == 3 ")
            pathInfo = treeView.get_path_at_pos(event.x, event.y)

            if pathInfo is not None:
                path, column, xCoord, yCoord = pathInfo
                treeIter = model.get_iter(path)
                self.focusedTreeIter = treeIter
                # print(model[treeIter][0])
                if model.iter_has_child(treeIter):
                    self.workshopMenu.show_all()
                    self.workshopMenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

                elif not model.iter_has_child(treeIter):
                    self.itemMenu.show_all()
                    self.itemMenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

            else:
                self.blankMenu.show_all()
                self.blankMenu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def addNewWorkshop(self, workshopName, vmName):
        logging.debug("addNewWorkshop() initiated: " + str(workshopName) + " " + str(vmName))
        self.session.addWorkshop(workshopName, vmName)
        self.workshopTree.addNode(workshopName, vmName)

        self.softSave()
        self.hardSave()

    def addNewVM(self, vmName):
        logging.debug("addNewVM() initiated: " + str(vmName))
        self.session.addVM(vmName)
        self.workshopTree.addChildNode(self.focusedTreeIter, VM_TREE_LABEL + vmName)

        self.softSave()
        self.hardSave()

    def addNewMaterial(self, materialAddress):
        logging.debug("addNewMaterial() initiated: " + str(materialAddress))
        holdName = os.path.basename(materialAddress)
        self.session.addMaterial(materialAddress)
        logging.debug("adding a child node: " + str(self.focusedTreeIter) + " " + str(MATERIAL_TREE_LABEL + holdName))
        self.workshopTree.addChildNode(self.focusedTreeIter, MATERIAL_TREE_LABEL + holdName)

    def cloneWorkshopActionEvent(self, menuItem):
        logging.debug("cloneWorkshopActionEvent() initiated: " + str(menuItem))
        if self.session.currentWorkshop is None:
            WarningDialog(self.window, "You must select a workshop before you can run the workshop.")
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

    def startVMsActionEvent(self, menuItem):
        logging.debug("startVMsActionEventActionEvent() initiated: " + str(menuItem))
        if self.session.currentWorkshop is None:
            WarningDialog(self.window, "You must select a workshop before you can run the workshop.")
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

    def poweroffVMsActionEvent(self, menuItem):
        logging.debug("poweroffVMsActionEvent() initiated: " + str(menuItem))
        if self.session.currentWorkshop is None:
            WarningDialog(self.window, "You must select a workshop before you can run the workshop.")
            return

        workshopName = self.session.currentWorkshop.filename
        command = "python -u \"" + VM_POWEROFF_FILE_PATH + "\" \"" + os.path.join(WORKSHOP_CONFIG_DIRECTORY,
                                                                                  workshopName + ".xml\"")
        logging.debug("poweroffVMsActionEvent(): instantiating ProcessDialog")
        pd = ProcessDialog(command)
        logging.debug("poweroffVMsActionEvent(): running ProcessDialog")
        pd.run()
        pd.destroy()
        logging.debug("poweroffVMsActionEvent(): returned from ProcessDialog")

    def addWorkshopActionEvent(self, menuItem):
        logging.debug("addWorkshopActionEvent() initiated: " + str(menuItem))
        workshopDialog = EntryDialog(self, "Enter a workshop name.")
        workshopText = None

        while workshopDialog.status != True:
            response = workshopDialog.run()
            workshopText = workshopDialog.entryText
        workshopDialog.destroy()

        if workshopText != None:
            vmDialog = ListEntryDialog(self, "Enter a VM name.")
            vmText = None

            while not vmDialog.status == True:
                response = vmDialog.run()
                vmText = vmDialog.entryText
            vmDialog.destroy()

        if workshopText != None and vmText != None:
            self.addNewWorkshop(workshopText, vmText)
        self.superMenu.refreshActionEvent(self.session.workshopList)

    def removeWorkshopActionEvent(self, menuItem):
        logging.debug("removeWorkshopActionEvent() initiated: " + str(menuItem))
        d = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL,
                              "Are you sure you want to permanently delete this workshop?")
        response = d.run()
        d.destroy()

        if response == Gtk.ResponseType.OK:
            model = self.workshopTree.treeStore
            self.session.removeWorkshop()
            model.remove(self.focusedTreeIter)
        self.superMenu.refreshActionEvent(self.session.workshopList)

    def addMaterialActionEvent(self, menuItem):
        logging.debug("addMaterialActionEvent() initiated: " + str(menuItem))
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
                                       Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.addNewMaterial(dialog.get_filename())
        dialog.destroy()

    def addVMActionEvent(self, menuItem):
        logging.debug("addVMActionEvent() initiated: " + str(menuItem))
        vmDialog = ListEntryDialog(self, "Enter a VM name.")
        vmText = None

        while not vmDialog.status == True:
            response = vmDialog.run()
            vmText = vmDialog.entryText
        vmDialog.destroy()

        if vmText != None:
            self.addNewVM(vmText)

    def removeVMActionEvent(self, menuItem):
        logging.debug("removeVMActionEvent() initiated: " + str(menuItem))
        model = self.workshopTree.treeStore
        if self.session.currentVM != None:
            if len(self.session.currentWorkshop.vmList) > 1:
                self.session.removeVM()
                self.isRemoveVM = True
                model.remove(self.focusedTreeIter)
            else:
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK,
                                           "Cannot delete the last VM in a Workshop.")
                dialog.run()
                dialog.destroy()

        elif self.session.currentMaterial != None:
            self.session.removeMaterial()
            self.isRemoveVM = True
            model.remove(self.focusedTreeIter)

    # Event, executes when export is called
    def exportWorkshopActionEvent(self, menuItem):
        logging.debug("exportWorkshopActionEvent() initiated: " + str(menuItem))
        matchFound = self.session.getAvailableVMs()

        if not matchFound:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK,
                                       "Not all VM's for this workshop are registered.")
            dialog.run()
            dialog.destroy()
            return

        dialog = Gtk.FileChooserDialog("Please choose a folder.", self,
                                       Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                                             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        folderPath = None
        if response != Gtk.ResponseType.OK:
            dialog.destroy()
            return
        else:  # response == Gtk.ResponseType.OK
            # Save before export otherwise xml file will not contain materials!
            self.session.hardSave()

            folderPath = os.path.join(dialog.get_filename(), self.session.currentWorkshop.filename)
            dialog.destroy()
            # TODO: Transform the spinner into the ProcessOutput Window
            # Following this protocol: any functions to which this spinner dialog can call run, but must call hide (not destroy!)
            # when finished. These will likely be functions that start threads.
            # TODO: need to make the spinnerDialog take a thread and start it after the dialog is shown, otherwise, this could lead to an undestroyable dialog
            spinnerDialog = SpinnerDialog(self, "Exporting to EBX archive, this may take a few minutes...")
            GLib.idle_add(spinnerDialog.set_title, "Exporting...")
            self.session.exportWorkshop(folderPath, spinnerDialog)
            spinnerDialog.run()
            # this destroy will happen only after any hides; hides be called after the destroy
            spinnerDialog.destroy()
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                                       self.session.currentWorkshop.filename + " export complete\r\nFile created in: " + str(
                                           folderPath))
            dialog.run()
            dialog.destroy()

    # Event, executes when import is called
    def importActionEvent(self, menuItem):
        logging.debug("importVMActionEvent() initiated")
        dialog = Gtk.FileChooserDialog("Please select a EBX archive to import.", self,
                                       Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            zipPath = dialog.get_filename()
            # get path for temporary directory to hold uncompressed files
            tempPath = os.path.join(os.path.dirname(zipPath), "creatorImportTemp",
                                    os.path.splitext(os.path.basename(zipPath))[0])
            baseTempPath = os.path.join(os.path.dirname(zipPath), "creatorImportTemp")
            dialog.destroy()

            # First we need to unzip the import file to a temp folder
            # Following this protocol: any functions to which this spinner dialog can call run, but must call hide (not destroy!)
            # when finished. These will likely be functions that start threads.
            # TODO: need to make the spinnerDialog take a thread and start it after the dialog is shown, otherwise, this could lead to an undestroyable dialog
            spinnerDialog = SpinnerDialog(self, "Preparing to decompress EBX archive")
            self.session.importUnzip(zipPath, spinnerDialog)
            spinnerDialog.show()

            ovaList = []
            xmlList = []
            materialList = []
            rdpList = []
            # Get all files that end with .ova
            if os.path.exists(tempPath):
                baseFiles = os.listdir(tempPath)
                for filename in baseFiles:
                    if filename.endswith(".ova"):
                        ovaList.append(filename)
                    elif filename.endswith(".xml"):
                        xmlList.append(filename)
            materialsPath = os.path.join(tempPath, "Materials")
            logging.debug("importActionEvent(): Materials folder to search: " + str(materialsPath))
            if os.path.exists(materialsPath):
                materialsFiles = os.listdir(materialsPath)
                logging.debug("importActionEvent(): Materials to import: " + str(materialsFiles))
                for filename in materialsFiles:
                    logging.debug("importActionEvent(): Adding material to workshop: " + str(filename))
                    materialList.append(filename)
            rdpPath = os.path.join(tempPath, "RDP")
            if os.path.exists(rdpPath):
                rdpFiles = os.listdir(rdpPath)
                for filename in rdpFiles:
                    rdpList.append(filename)
            vmNum = 1
            for ova in ovaList:
                prog = float(float(vmNum) / len(ovaList))
                logging.debug("importActionEvent(): Importing " + str(ova) + " into VirtualBox...")
                GLib.idle_add(spinnerDialog.setTitleVal, "Importing VMs")
                GLib.idle_add(spinnerDialog.setLabelVal, "Importing VM " + str(vmNum) + " of " + str(len(ovaList)))
                GLib.idle_add(spinnerDialog.setProgressVal, prog)
                #HERE is where
                pd = ProcessDialog(VBOXMANAGE_DIRECTORY + " import " + os.path.join(tempPath, ova) + " --options keepallmacs", granularity="char", capture="stderr")
                pd.run()
                vmNum = vmNum + 1
            spinnerDialog.destroy()

            for xml in xmlList:
                # here we need to parse the file in order to obtain the groupBaseName
                logging.debug("importActionEvent(): Found XML file: " + xml)
                shutil.copy2(os.path.join(tempPath, xml), WORKSHOP_CONFIG_DIRECTORY)
            self.filename = os.path.join(tempPath, xmlList[0])
            logging.debug("importActionEvent(): Loading config file XML data: " + self.filename)
            tree = ET.parse(self.filename)
            root = tree.getroot()
            vmset = root.find('testbed-setup').find('vm-set')
            currXMLWorkshopGroupName = vmset.find('base-groupname').text
            logging.debug(
                "importActionEvent(): using workshop group name for directory creation: " + currXMLWorkshopGroupName)

            holdMatPath = os.path.join(WORKSHOP_MATERIAL_DIRECTORY, currXMLWorkshopGroupName)
            if not os.path.exists(holdMatPath):
                os.makedirs(holdMatPath)

            for material in materialList:
                logging.debug("importActionEvent(): Processing file " + str(material))
                logging.debug("importActionEvent(): Checking for " + os.path.join(holdMatPath, material))
                if not os.path.exists(os.path.join(holdMatPath, material)):
                    logging.debug("importActionEvent(): copying file " + str(
                        os.path.join(tempPath, "Materials", material)) + " to " + str(material))
                    shutil.copy2(os.path.join(tempPath, "Materials", material), holdMatPath)

            holdRDPPath = os.path.join(WORKSHOP_RDP_DIRECTORY, currXMLWorkshopGroupName)
            if not os.path.exists(holdRDPPath):
                os.makedirs(holdRDPPath)
            for rdp in rdpList:
                if not os.path.exists(holdRDPPath + rdp):
                    shutil.copy2(os.path.join(tempPath, "RDP", rdp), holdRDPPath)

            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                                       "Workshop import complete.")
            dialog.run()
            dialog.destroy()

            # reload all xml files and create a new display
            self.workshopTree.clearTreeStore()
            self.session.loadXMLFiles(WORKSHOP_CONFIG_DIRECTORY)
            self.workshopTree.populateTreeStore(self.session.workshopList)

            shutil.rmtree(baseTempPath, ignore_errors=True)
            self.superMenu.refreshActionEvent(self.session.workshopList)

        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

    # Executes when the window is closed
    def on_delete(self, event, widget):
        logging.debug("on_delete() initiated: " + str(event) + " " + str(widget))
        self.managerBox.destroy_process()
        self.fullSave()

    def getDownloadIndex(self, location):
        logging.debug("Attempt to download index file")
        if location == None:
            location = ONLINE_INDEX_FILE
        try:
            self.downloadIndex = urllib2.urlopen(location).read()
            return True
        except:
            WarningDialog(self, "Could not fetch workshop index file.  Check your network connection and the location.")
            return False

    def downloadFile(self, url, workshopName):
        logging.debug("initiating download with progress spinner dialog")
        try:
            spinnerDialog = SpinnerDialog(self, "Preparing to download workshop...")
            self.session.downloadWorkshop(url, workshopName, spinnerDialog)
            spinnerDialog.destroy()
            return True
        except:
            WarningDialog(self, "Could not download workshop file.  Check your network connection.")
            return False

    def download(self, menuItem):
        logging.debug("beginning new workshop download")
        if (self.downloadIndex == None):
            if not self.getDownloadIndex(None):
                return
        downloadDialog = DownloadDialog(self, "Select a workshop to download.", self.downloadIndex)
        downloadText = None

        while not downloadDialog.status:
            if downloadDialog.status is False:
                downloadDialog.destroy()
                return
            downloadDialog.run()
            downloadText = downloadDialog.xmlString
        downloadDialog.destroy()

        if downloadText is None:
            return
        elif self.session.isWorkshop(downloadDialog.entryText):
            WarningDialog(self, "Workshop already exists.")
            return

        if not self.downloadFile(self.session.getDownloadLink(downloadText, downloadDialog.entryText),
                                 downloadDialog.entryText):
            return

        zipPath = str(self.session.downloadedZip)
        if not os.path.isfile(zipPath):
            WarningDialog(self, "Error Downloading File, please retry")
            return

        # First we need to unzip the import file to a temp folder
        spinnerDialog = SpinnerDialog(self, "Preparing to unzip files")
        self.session.unzip(zipPath, spinnerDialog)
        spinnerDialog.destroy()

        spinnerDialog = SpinnerDialog(self, "Preparing to import files")
        self.session.importParseWithSpinner(os.path.join(WORKSHOP_TMP_DIRECTORY, downloadDialog.entryText), spinnerDialog)
        spinnerDialog.destroy()

        # # reload all xml files and create a new display
        self.workshopTree.clearTreeStore()
        self.session.loadXMLFiles(WORKSHOP_CONFIG_DIRECTORY)
        self.workshopTree.populateTreeStore(self.session.workshopList)
        shutil.rmtree(WORKSHOP_TMP_DIRECTORY, ignore_errors=True)
        os.remove(zipPath)
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                                   "Workshop download complete.")
        dialog.run()
        dialog.destroy()
        self.superMenu.refreshActionEvent(self.session.workshopList)
