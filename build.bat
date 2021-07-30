call venv\Scripts\activate.bat
echo [102mRUN PYINSTALLER[0m
pyinstaller mainwindow.spec
echo [102mCREATE SCHEMES DIRECTORY[0m
mkdir dist\mainwindow\schemes
echo [102mCREATE INFO.LOG FILE[0m
break > dist\mainwindow\log\info.log
echo [102mCOPY CONFIGS[0m
copy configs dist\mainwindow
call venv\Scripts\deactivate