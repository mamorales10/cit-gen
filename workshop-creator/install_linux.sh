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
    export VBOX_SDK_PATH=`pwd`/../workshop-manager/bin/VirtualBoxSDK-5.1.20-114628/sdk/
fi  
if [ -z "$VBOX_PROGRAM_PATH" ]; then
    echo "Warning: VBOX_PROGRAM_PATH was not set, using: /usr/lib/virtualbox/" 
    export VBOX_PROGRAM_PATH=/usr/lib/virtualbox/
fi 

apt-get install python-gi
apt-get install python-pip
apt-get install libgirepository1.0-dev

pip install virtualenv
virtualenv $VENV_NAME

source ./$VENV_NAME/bin/activate
#creator dependencies
pip install pygobject
pip install lxml
pip install vext
pip install vext.gi

#manager dependencies
pip install flask
pip install pyvbox
pip install gevent
pip install gevent-socketio
cd ../workshop-manager/bin/VirtualBoxSDK-5.1.20-114628/sdk/installer/
python vboxapisetup.py install
cd ../../../../../workshop-creator/

#Generate the script 
echo "#!/usr/bin/env bash" > start_creator.sh
echo "#The name of the container used during installation" >> start_creator.sh
echo VENV_NAME=$VENV_NAME >> start_creator.sh
echo >> start_creator.sh
echo "#Activate the container and invoke the gui" >> start_creator.sh
echo source ./$VENV_NAME/bin/activate >> start_creator.sh
echo "#These variables are set based on their values when the install script is executed. Re-set values as needed." >> start_creator.sh
echo export VBOX_INSTALL_PATH=$VBOX_INSTALL_PATH >> start_creator.sh
echo export VBOX_SDK_PATH=$VBOX_SDK_PATH >> start_creator.sh
echo export VBOX_PROGRAM_PATH=$VBOX_PROGRAM_PATH >> start_creator.sh
echo cd bin >> start_creator.sh
echo gsettings set com.canonical.Unity integrated-menus true >> start_creator.sh
echo python workshop_creator_gui.py >> start_creator.sh
echo gsettings set com.canonical.Unity integrated-menus false >> start_creator.sh


chmod 755 start_creator.sh
echo
echo
echo Type: ./start_creator.sh to start the workshop-creator-gui

