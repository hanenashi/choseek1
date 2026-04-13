@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [FAIL] Virtual environment not found.
    echo [HINT] Run install.bat first.
    goto :end
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [FAIL] Could not activate virtual environment.
    goto :end
)

python run.py
if errorlevel 1 (
    echo.
    echo [FAIL] App exited with an error.
)

:end
endlocal
pause