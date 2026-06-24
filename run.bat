@echo off
chcp 65001 >nul
title CursorKeep

if exist "CursorKeep.exe" (
    start "" "CursorKeep.exe"
) else if exist "dist\CursorKeep.exe" (
    start "" "dist\CursorKeep.exe"
) else (
    echo.
    echo CursorKeep.exe este neexistuje.
    echo Najprv spusti build_windows.bat (len raz).
    echo.
    pause
)