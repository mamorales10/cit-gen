# The Collaborative Innovation Testbed (Rapid Cyber Range)
## Table of Contents
* [Description](#description)
* [Installation](#installation)
* [Create and Run a Workshop](#create-and-run-a-workshop)
* [Linux Live Disc](#linux-live-disc)
* [CIT-RCR Construct Details](#cit-rcr-construct-details)

### Description
CIT-RCR uses the Flask python microframework as the web server gateway interface (WSGI) application.
This provides similar functionality as a fast common gateway interface (FCGI) application that allows 
multiple, concurrent connections to the web application.

Gevent is used to host the standalone flask WSGI container. This handles the concurrent WSGI behavior. It uses 
greenlet to provide high-level synchronous API on top of libev event loop. 

CIT-RCR is composed of two main components: The Workshop Creator and the Workshop Manager.

### Installation
CIT-RCR has been tested on:
* Windows 7+ (32 and 64-bit), Windows Server 2012 (64-bit)
* Ubuntu 16.04 LTE (64-bit)

##### Requirements
You must install the following manually:
* Python 2.x (tested with [v2.7](https://www.python.org/download/releases/2.7/))
* VirtualBox > 5.0 and matching VirtualBox API and Extensions Pack (tested with [v5.1.10](https://www.virtualbox.org/wiki/Downloads))

These are automatically installed with the included install script
* VirtualEnv [v15.1.0](https://virtualenv.pypa.io/en/stable/)
* LXML [v4.0.0](http://lxml.de/changes-4.0.0.html)
* Flask [v0.12](http://pypi.python.org/pypi/Flask/0.12)
* PyGI based on [this Windows Installer](https://sourceforge.net/projects/pygobjectwin32/files/pygi-aio-3.10.2-win32_rev18-setup.exe/download)

##### Windows Instructions
In the directory where you extracted CIT-RCR:
```
cd workshop-creator
./install_win.bat
```
To create and run a workshop, proceed to [Create and Run a Workshop](#create-and-run-a-workshop).

##### Linux
In the directory where you extracted CIT-RCR:
```
sudo -s
cd workshop-creator
```
Set the following environment variables

* VBOX_INSTALL_PATH
* VBOX_SDK_PATH
* VBOX_PROGRAM_PATH

For example, 
```
export VBOX_INSTALL_PATH=$(which virtualbox)
export VBOX_SDK_PATH=`pwd`/bin/VirtualBoxSDK-5.1.20-114628/sdk/
export VBOX_PROGRAM_PATH=/usr/lib/virtualbox/
```
Now run the installer
```
source ./install_linux.sh
```
To create and run a workshop, proceed to [Create and Run a Workshop](#create-and-run-a-workshop).

### Create and Run a Workshop
CIT-RCR runs on a flask webserver and a backend monitor for virtualbox VMs.
Before starting, install CIT-RCR as described [here](#installation).

1. Ensure that you have one or more virtual machines installed and that they have at least one snapshot (only the latest is used).
    
    **Note:** On Linux, you must install VMs with administrator priviledges (i.e., instantiate VirtualBox as root or using sudo), otherwise remote display and other features will not work. 
2. Start the GUI by executing the following commands in a terminal:

    Windows:
    ```
    cd workshop-creator
    start_creator.bat
    ```
    Linux:
    ```
    sudo -s
    cd workshop-creator
    ./start_creator.sh
    ```
3. Right-click in the Workshops pane and select "New Workshop" and then enter a workshop name.
4. Select a virtual machine from the list and click the OK button. This will add a new entry in the Workshops pane.
5. Add any additional VMs and Materials by selecting your workshop and using the context (right-click) menu. 
6. Configure workshop settings on the right Panel to include the number of clones, usage of linked clones (true value is recommended), and the IP address where users will connect to access the workshop.
7. Expand the Workshop entry and select a specific VM or Material to configure settings such as VRDP, internal network names, display ports.
8. Ensure that at least one VM in your workshop has VRDP enabled.
9. Right click on your workshop and select the Create Clones option.
10. Right click on your workshop and select the Start VMs option.
11. Click on the Manager tab and toggle the Manager switch to ON.
12. Open a browser and navigate to the following URL:
```
http://localhost:8080
```
If accessing the CIT-RCR server from the network (e.g., when hosting workshops for participants), from the remote machine's browser, substitute `localhost` for the IP address of the machine running the server.

### Linux Live Disc
A live disc pre-installed with CIT-RCR is available [here](https://goo.gl/nRrR2v).
The following are the steps for running CIT-RCR on the live disc.
##### DHCP Service Configuration (Optional)
The DHCP service is pre-configured. To enable the DHCP server execute the following steps:

1. If needed, modify the following files to assign the dhcp server interface and network range (enp0s3 is the default interface):
```
/etc/dhcp/dhcpd.conf
/etc/default/isc-dhcp-server
```
2. If needed, modify the following file to set a static IP address to the interface serving DHCP:
```
/etc/network/interfaces
```
3. Start the dhcp service:
```
sudo service isc-dhcp-server start
```

##### VNC Server Configuration (Optional)
To enable the pre-installed Ubuntu VNC server follow instructions [here](https://www.howtoforge.com/configure-remote-access-to-your-ubuntu-desktop)

##### SSH Server configuration (Optional)
To enable the SSH service execute the following steps:

1. Start the ssh server
```
sudo service ssh start
```

##### VPN Server (Optional)
The VPN server is pre-configured. To enable the PPTPD VPN server execute the following steps:

1. If needed, change the IP addresses assigned to the server node and connected clients by modifying the following
```
/etc/pptpd.conf
```
2. If needed, change the DNS entries (lines with *ms-dns*) by modifying IP addresses in the following file
```
/etc/ppp/pptpd-options
```
3. Specify users, credentials, and IP address mappings in the following file:
```
/etc/ppp/chap-secrets
```
4. Start the pptpd service:
```
sudo service pptpd start
```

##### Start CIT-RCR (Required)
1. Open a terminal window and execute the following commands:
```
sudo -s
cd /root/cit-rcr/workshop-creator
./start_creator.sh
```
To create and run a workshop, proceed to [Create and Run a Workshop](#create-and-run-a-workshop).
  
### CIT-RCR Construct Details
##### Workshop Creator
The Workshop Creator automates the creation of workshop units (sets of VMs that compose a cybersecurity scenario). This includes the cloning process.
During the cloning process, this component adjusts VRDP ports and internal
network adapter names so that each group is isolated and uniquely accessible by
participants.

The Workshop Creator GUI provides a graphical interface to design workshop units and modify their parameters.  The user can then run the Workshop Creator script via the interface, eliminating the need to set command line parameters manually.

To run the Workshop Creator GUI, first install it by following instruction below. 
Afterwards, open a terminal and type the following command:
    
   Windows:
```
cd workshop-creator
start_creator.bat
```
   Linux:
```
cd workshop-creator
./start_creator.sh
```

The Workshop Creator can also be used without the graphical interface by running the various scripts in the following scripts:
```
workshop-creator/bin/workshop-creator.py (clones VMs and groups them into Workshop Units)
workshop-creator/bin/workshop-start.py (starts (headless mode) VMs in Workshop Units)
workshop-creator/bin/workshop-rdp.py (creates Remote Desktop files for VRDP-enabled VMs in Workshop Units)
workshop-creator/bin/workshop-poweroff.py (turns off VMs in Workshop Units)
workshop-creator/bin/workshop-restore.py (restores most recent snapshot of VMs in Workshop Units - only those not in a run state)
``` 
**Note**: All of these scripts read a standard XML file as input (samples are provided in the `workshop-creator/sample_configs` folder. 

##### Workshop Manager

The Workshop Manager component of CIT-RCR is a multi-threaded process that
monitors VRDP connections for each workshop unit. It also contains a web service
with a simple front-end that is implemented using the Flask micro web development
framework. When participants navigate to the front-end they are shown the
VRDP-enabled workshop units (those that are available and not currently in use).
The front-end also provides participants with a unique connection string (IP
address and VRDP port pair) to use in a remote desktop client, such as MS-RDP on
Windows, Mac OS, iOS, and rdesktop on Linux.

When a participant connects to a a unit, it becomes unavailable and will no
longer be shown in the web interface. After a participant disconnects from the
unit, the system will automatically restore the associated VMs from snapshot
and make it available once again.

The Workshop Manager is integrated into the workshop creator GUI, but it can also be instantiated without the graphical interface by executing the following commands: 

   Windows:
```
cd workshop-manager
start_manager.bat
```
   Linux:
```
sudo -s
cd workshop-manager
./start_manager.sh
```

##### Workshop Units

The CIT-RCR uses the VirtualBox API to monitor and update groups of VMs (that compose a workshop unit). Users may connect to these units using remote desktop. When a user disconnects, CIT-RCR will restore all VMs in a unit from the most recent snapshot.
