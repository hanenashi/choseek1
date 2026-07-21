@echo off
setlocal

cd /d "%~dp0"

set "APP_DIR=%CD%"
set "LAUNCHER=%APP_DIR%\choseek1-open.bat"
set "ICON=%APP_DIR%\choseek1.ico"
set "MENU_TEXT=Open folder in choseek1"

if not exist "%LAUNCHER%" (
    echo [FAIL] Missing launcher: %LAUNCHER%
    goto :end
)

echo [INFO] Adding choseek1 to the folder context menu...

reg add "HKCU\Software\Classes\Directory\shell\choseek1" /ve /d "%MENU_TEXT%" /f >nul
reg add "HKCU\Software\Classes\Directory\shell\choseek1" /v "Icon" /d "%ICON%" /f >nul
reg add "HKCU\Software\Classes\Directory\shell\choseek1\command" /ve /d "\"%LAUNCHER%\" \"%%1\"" /f >nul

reg add "HKCU\Software\Classes\Directory\Background\shell\choseek1" /ve /d "%MENU_TEXT%" /f >nul
reg add "HKCU\Software\Classes\Directory\Background\shell\choseek1" /v "Icon" /d "%ICON%" /f >nul
reg add "HKCU\Software\Classes\Directory\Background\shell\choseek1\command" /ve /d "\"%LAUNCHER%\" \"%%V\"" /f >nul

echo.
echo [OK] Context menu installed.
echo [INFO] Right-click a folder, or empty space inside a folder, then choose "%MENU_TEXT%".

:end
endlocal
pause
