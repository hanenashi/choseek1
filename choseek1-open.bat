@echo off
setlocal

set "TARGET_FOLDER=%~1"
if "%TARGET_FOLDER%"=="" set "TARGET_FOLDER=%CD%"

cd /d "%~dp0"

if exist "dist\choseek1\choseek1.exe" (
    start "" "%~dp0dist\choseek1\choseek1.exe" "%TARGET_FOLDER%"
    goto :end
)

if not exist ".venv\Scripts\python.exe" (
    echo [FAIL] Virtual environment not found. Run install.bat first.
    pause
    goto :end
)

start "" "%~dp0.venv\Scripts\python.exe" "%~dp0run.py" "%TARGET_FOLDER%"

:end
endlocal
