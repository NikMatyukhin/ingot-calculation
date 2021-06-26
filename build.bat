call venv\Scripts\activate.bat
pyinstaller mainwindow.spec
mkdir dist\mainwindow\schemes
break > dist\mainwindow\log\info.log
call venv\Scripts\deactivate