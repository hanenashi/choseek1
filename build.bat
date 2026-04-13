@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo [FAIL] Virtual environment not found. Run install.bat first.
    goto :end
)

echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [INFO] Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 goto :fail

echo [INFO] Cleaning up old builds...
if exist "build" rmdir /s /q "build"
if exist "dist\choseek1" rmdir /s /q "dist\choseek1"

echo [INFO] Building choseek1.exe...
:: --noconfirm : overwrites previous output
:: --onedir    : creates a folder with the exe and dlls (faster to load than onefile)
:: --windowed  : hides the black console window
:: --icon      : sets the icon of the .exe file itself
:: --add-data  : bundles the icon so the app can load it for the window/help menu at runtime
pyinstaller --noconfirm --onedir --windowed --icon="choseek1.ico" --add-data="choseek1.ico;." --name="choseek1" run.py
if errorlevel 1 goto :fail

echo.
echo [OK] Build complete!
echo [INFO] You can find your compiled app in the "dist\choseek1" folder.
echo [INFO] You can ZIP the "choseek1" folder and share it.
goto :end

:fail
echo.
echo [FAIL] The build process encountered an error.
:end
endlocal
pause