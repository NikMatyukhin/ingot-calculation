call venv\Scripts\activate.bat
echo RUN PYINSTALLER
pyinstaller mainwindow.spec --noconfirm
echo CREATE SCHEMES DIRECTORY
mkdir dist\mainwindow\schemes
echo CREATE INFO.LOG FILE
break > dist\mainwindow\log\info.log
echo COPY CONFIGS
copy configs dist\mainwindow
call venv\Scripts\deactivate
cd dist
echo ARCHIVING FILES
del *.zip
7z a -tzip new_version.zip mainwindow