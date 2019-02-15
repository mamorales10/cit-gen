REM name the container that will be created
set VENV_NAME=manager-container

REM Make sure path to pip is set correctly
pip install virtualenv
virtualenv %VENV_NAME%

(%VENV_NAME%\Scripts\activate & pip install flask & pip install pyvbox & pip install gevent & pip install gevent-socketio & pip install pypiwin32 & cd bin\VirtualBoxSDK-5.1.20-114628\sdk\installer\ & python vboxapisetup.py install & cd ..\..\..\..\ & %VENV_NAME%\Scripts\deactivate
REM Now create the file that will start the manager
echo REM the name of the container used during installation > start_manager.bat
echo set VENV_NAME=manager-container >> start_manager.bat
echo. >> start_manager.bat
echo REM activate the container and invoke the manager >> start_manager.bat
echo %VENV_NAME%\Scripts\activate ^& cd bin ^& python instantiator.py >> start_manager.bat
echo Type: start-manager.bat to start the workshop-manager
)