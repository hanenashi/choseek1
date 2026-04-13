@echo off
setlocal

cd /d "%~dp0"

echo [INFO] Creating virtual environment...
py -m venv .venv
if errorlevel 1 goto :venv_fail

echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 goto :activate_fail

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 goto :pip_fail

echo [INFO] Installing requirements...
pip install -r requirements.txt
if errorlevel 1 goto :req_fail

echo.
echo [OK] Install complete.
echo [INFO] Run the app with run.bat
goto :end

:venv_fail
echo.
echo [FAIL] Could not create virtual environment.
echo [HINT] Make sure Python launcher "py" is installed and on PATH.
goto :end

:activate_fail
echo.
echo [FAIL] Could not activate virtual environment.
goto :end

:pip_fail
echo.
echo [FAIL] Pip upgrade failed.
goto :end

:req_fail
echo.
echo [FAIL] Requirements installation failed.
goto :end

:end
endlocal
pause