@echo off
setlocal

set PYTHON_BIN=python
if exist env\Scripts\python.exe set PYTHON_BIN=env\Scripts\python.exe

%PYTHON_BIN% manage.py seed_demo_data %*
set EXIT_CODE=%ERRORLEVEL%

if not "%EXIT_CODE%"=="0" (
    exit /b %EXIT_CODE%
)

endlocal
