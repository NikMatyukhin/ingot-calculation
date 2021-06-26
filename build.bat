call venv\Scripts\activate.bat
pyinstaller mainwindow.spec
cd dist\mainwindow
mkdir schemes
break > dist\mainwindow\log\info.log
call venv\Scripts\deactivate