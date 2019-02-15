@echo off
REM Edit the following variables according to python installation
set PYTHONARCH=64

REM ask user for version of python
set /P version64="Is your python installation Python 2.7.* 64-bit? (Y/N): "
IF NOT "%version64%"=="Y" IF NOT "%version64%"=="y" (
set PYTHONARCH=32
echo *************************************************************************************************
echo Sorry, this version of Python is currently not supported. Please install Python 2.7 64-bit.
echo *************************************************************************************************
pause
exit
)

REM set directory to place Gtk files
set PYTHONPACKAGES_PATH=Lib\site-packages\

REM name the container that will be created
set VENV_NAME=creator-container

REM install and start the venv container
pip install virtualenv
virtualenv "%VENV_NAME%"

IF %PYTHONARCH%==32 (
echo Processing using a 32-bit python27 installation
%VENV_NAME%\Scripts\activate & pip install lxml & xcopy python27-32bit-gtk3\* "%VENV_NAME%\%PYTHONPACKAGES_PATH%" /E /Y & pip install flask & pip install pyvbox & pip install gevent & pip install gevent-socketio & pip install pypiwin32 & cd ..\workshop-manager\bin\VirtualBoxSDK-5.1.20-114628\sdk\installer\ & python vboxapisetup.py install & cd ..\..\..\..\..\workshop-creator\ & %VENV_NAME%\Scripts\deactivate
REM Now create the file that will start the gui
echo REM the name of the container used during installation > start_creator.bat
echo set VENV_NAME=creator-container >> start_creator.bat
echo. >> start_creator.bat
echo REM activate the container and invoke the gui >> start_creator.bat
echo %VENV_NAME%\Scripts\activate ^& cd bin ^& python workshop_creator_gui.py ^& deactivate ^& cd ..>> start_creator.bat
echo Type: start_creator.bat to start the workshop-creator-gui
) ELSE (
echo Processing using a 64-bit python27 installation
%VENV_NAME%\Scripts\activate & pip install lxml & xcopy python27-64bit-gtk3\* "%VENV_NAME%" /E /Y & pip install flask & pip install pyvbox & pip install gevent & pip install gevent-socketio & pip install pypiwin32 & cd ..\workshop-manager\bin\VirtualBoxSDK-5.1.20-114628\sdk\installer\ & python vboxapisetup.py install & cd ..\..\..\..\..\workshop-creator\ & %VENV_NAME%\Scripts\deactivate
REM Now create the file that will start the gui
echo REM the name of the container used during installation > start_creator.bat
echo set VENV_NAME=creator-container >> start_creator.bat
echo. >> start_creator.bat
echo REM activate the container and invoke the gui >> start_creator.bat
echo %VENV_NAME%\Scripts\activate ^& cd bin ^& python workshop_creator_gui.py ^& deactivate ^& cd .. >> start_creator.bat
echo Type: start_creator.bat to start the workshop-creator-gui
)

