import os
# TODO: make this file editable through the GUI somehow
# OS-specific constants
if os.name == 'nt':
    VBOXMANAGE_DIRECTORY = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
    POSIX = False
else:
    VBOXMANAGE_DIRECTORY = "/usr/bin/vboxmanage"
    POSIX = True
# GUI constants
BOX_SPACING = 0
PADDING = 1

WORKSHOP_CONFIG_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "workshop_creator_gui_resources", "workshop_configs")
WORKSHOP_MATERIAL_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "workshop_creator_gui_resources", "workshop_materials")
WORKSHOP_RDP_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "workshop_creator_gui_resources", "workshop_rdp")
STATIC_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "static")
# External files
VM_STARTER_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "workshop-start.py")
VM_POWEROFF_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "workshop-poweroff.py")
WORKSHOP_CREATOR_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "workshop-creator.py")
WORKSHOP_RDP_CREATOR_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "workshop-rdp.py")
WORKSHOP_RESTORE_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "workshop-restore.py")
WORKSHOP_TMP_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "workshop_creator_gui_resources", "creatorImportTemp")
MANAGER_SAVE_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..", "..", "workshop-manager", "bin", "WorkshopData")
MANAGER_BIN_DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..", "..", "workshop-manager", "bin")
# Labels
VM_TREE_LABEL = "V: "
MATERIAL_TREE_LABEL = "M: "
# Online Files
ONLINE_INDEX_FILE = "https://drive.google.com/uc?export=download&id=1cDKdt6sBJujW53gaJEiGtz0XsXld44gz"
DOWNLOAD_LOCATION = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "workshop_creator_gui_resources")
# Download Error Message
DOWNLOAD_ERROR = "Could not download file.  Please try again."
