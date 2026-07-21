@echo off
setlocal

echo [INFO] Removing choseek1 from the folder context menu...

reg delete "HKCU\Software\Classes\Directory\shell\choseek1" /f >nul 2>nul
reg delete "HKCU\Software\Classes\Directory\Background\shell\choseek1" /f >nul 2>nul

echo.
echo [OK] Context menu removed.

endlocal
pause
