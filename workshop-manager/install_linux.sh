#!/usr/bin/env bash

#environment variables have default values, but should be set before calling the installer
if [ -z "$VENV_NAME" ]; then
    echo "Warning: VENV_NAME was not set, using: creator-container" 
    VENV_NAME=creator-container
fi
#For now, assume the user must specify these before the install is executed
if [ -z "$VBOX_INSTALL_PATH" ]; then
    echo "Warning: VBOX_INSTALL_PATH was not set, using: $(which virtualbox)" 
    export VBOX_INSTALL_PATH=$(which virtualbox)
fi  
if [ -z "$VBOX_SDK_PATH" ]; then
    echo "Warning: VBOX_SDK_PATH was not set, using: ../workshop-manager/bin/VirtualBoxSDK-5.1.20-114628/sdk/" 
    export VBOX_SDK_PATH=../workshop-manager/bin/VirtualBoxSDK-5.1.20-114628/sdk/
fi  
if [ -z "$VBOX_PROGRAM_PATH" ]; then
    echo "Warning: VBOX_PROGRAM_PATH was not set, using: /usr/lib/virtualbox/" 
    export VBOX_PROGRAM_PATH=/usr/lib/virtualbox/
fi 

apt-get install python-pip
# Make sure path to pip is set correctly
pip install virtualenv
virtualenv $VENV_NAME
source ./$VENV_NAME/bin/activate
pip install flask
pip install pyvbox
pip install gevent
pip install gevent-socketio
VBOX_SDK_PATH=`pwd`/bin/VirtualBoxSDK-5.1.20-114628/sdk/
cd bin/VirtualBoxSDK-5.1.20-114628/sdk/installer/
python vboxapisetup.py install
cd ../../../../

echo "#!/usr/bin/env bash" > start_manager.sh
echo "#The name of the container used during installation" >> start_manager.sh
echo VENV_NAME=manager-container >> start_manager.sh
echo >> start_manager.sh
echo "#Activate the container and invoke the gui" >> start_manager.sh
echo source ./$VENV_NAME/bin/activate >> start_manager.sh
echo >> start_manager.sh
echo "#These variables are set based on their values when the install script is executed. Re-set values as needed." >> start_manager.sh
echo export VBOX_SDK_PATH=$VBOX_SDK_PATH >> start_manager.sh
echo export VBOX_PROGRAM_PATH=$VBOX_PROGRAM_PATH >> start_manager.sh
echo >> start_manager.sh
echo cd bin >> start_manager.sh
echo python instantiator.py >> start_manager.sh

chmod 755 start_manager.sh
echo
echo

echo Type: ./start_manager.sh to start the CIT-RCR Manager
