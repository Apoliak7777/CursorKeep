@echo off
chcp 65001 >nul
title CursorKeep - Vytvorenie .exe

echo.
echo ================================================
echo   CURSORKEEP - Vytvorenie samostatneho programu (v2.1)
echo ================================================
echo.
echo Tento skript nainstaluje vsetko potrebne a vytvori
echo samostatny .exe subor, ktory mozes spustit bez Pythonu.
echo.
echo Pozadovane kniznice: pyautogui, keyboard, pystray, pillow, pyinstaller
echo.
echo Stlac lubovolnu klavesu pre pokracovanie...
pause >nul

echo.
echo [1/3] Instalujem / aktualizujem potrebne knizlice...
pip install --upgrade pip
pip install pyautogui keyboard pystray pillow pyinstaller

if errorlevel 1 (
    echo.
    echo CHYBA pri instalacii! Skontroluj pripojenie na internet.
    pause
    exit /b
)

echo.
echo [2/3] Vytvaram samostatny .exe (onefile, bez konzoly)...
echo       (môze trvat 40-90 sekund)
pyinstaller --clean --noconfirm CursorKeep.spec

if errorlevel 1 (
    echo.
    echo CHYBA pri vytvarani .exe!
    pause
    exit /b
)

copy /Y dist\CursorKeep.exe .\CursorKeep.exe >nul 2>&1

echo.
echo [3/3] Hotovo!
echo.
echo ================================================
echo   .exe subor najdes tu:
echo   %cd%\CursorKeep.exe
echo   %cd%\dist\CursorKeep.exe
echo.
echo Odporucanie:
echo   1. Skopiruj CursorKeep.exe na plochu alebo do obľúbeného priečinka
echo   2. Vytvor si na ňom zástupcu (pravé tlačidlo → Odoslať na plochu)
echo   3. Spúšťaj ho kedykoľvek potrebuješ
echo.
echo POZNAMKA:
echo   Ak by si rebuildoval manualne, pouzi vzdy aktualny CursorKeep.spec
echo   (obsahuje collect-all pre pystray + PIL aby tray spolahlivo fungoval)
echo ================================================
echo.
pause