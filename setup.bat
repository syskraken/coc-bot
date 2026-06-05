@echo off
setlocal EnableDelayedExpansion
title COC Bot Installer - THE KRAKEN
color 0E

echo.
echo  ============================================================
echo    COC BOT INSTALLER - THE KRAKEN
echo  ============================================================
echo.
echo  This will install everything needed to run the bot:
echo    - Python 3.11
echo    - Required Python packages
echo    - Tesseract OCR
echo    - ADB (Android Debug Bridge)
echo.
echo  Press any key to begin...
pause >nul

:: ── Check internet ────────────────────────────────────────────
echo.
echo  [1/6] Checking internet connection...
ping -n 1 google.com >nul 2>&1
if errorlevel 1 (
    echo  [!] No internet connection detected.
    echo      Please connect and run this again.
    pause
    exit /b 1
)
echo  [OK] Internet connection OK.

:: ── Check / Install Python ────────────────────────────────────
echo.
echo  [2/6] Checking Python...

python --version >nul 2>&1
if not errorlevel 1 (
    echo  [OK] Python already installed.
    set PYTHON_CMD=python
    goto :python_done
)

:: Python not found - check default install locations
set PYTHON_LOCAL=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
set PYTHON_GLOBAL=C:\Python311\python.exe

if exist "%PYTHON_LOCAL%" (
    echo  [OK] Python found at local install path.
    set PYTHON_CMD="%PYTHON_LOCAL%"
    goto :python_done
)

if exist "%PYTHON_GLOBAL%" (
    echo  [OK] Python found at global install path.
    set PYTHON_CMD="%PYTHON_GLOBAL%"
    goto :python_done
)

:: Download and install Python
echo  [~] Python not found. Downloading Python 3.11...
curl -L --progress-bar -o "%TEMP%\python_installer.exe" https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
if errorlevel 1 (
    echo  [!] Download failed. Please install Python manually:
    echo      https://www.python.org/downloads/
    pause
    exit /b 1
)

echo  [~] Installing Python 3.11 (this may take a minute)...
"%TEMP%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1
if errorlevel 1 (
    echo  [!] Python installation failed.
    pause
    exit /b 1
)

:: Re-check after install
if exist "%PYTHON_LOCAL%" (
    set PYTHON_CMD="%PYTHON_LOCAL%"
    echo  [OK] Python 3.11 installed successfully.
    goto :python_done
)

echo  [!] Python installed but could not find python.exe.
echo      Please restart your PC and run setup.bat again.
pause
exit /b 1

:python_done

:: ── Upgrade pip ───────────────────────────────────────────────
echo.
echo  [3/6] Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo  [!] pip upgrade failed - continuing anyway...
) else (
    echo  [OK] pip up to date.
)

:: ── Install Python packages ───────────────────────────────────
echo.
echo  [4/6] Installing Python packages...
echo        opencv-python, numpy, Pillow, pytesseract
%PYTHON_CMD% -m pip install -r "%~dp0requirements.txt" --quiet
if errorlevel 1 (
    echo  [!] Package install failed.
    echo      Try manually: pip install -r requirements.txt
    pause
    exit /b 1
)
echo  [OK] All Python packages installed.

:: ── Check / Install Tesseract OCR ────────────────────────────
echo.
echo  [5/6] Checking Tesseract OCR...

if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo  [OK] Tesseract already installed.
    goto :tesseract_done
)

if exist "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe" (
    echo  [OK] Tesseract already installed (x86^).
    goto :tesseract_done
)

:: Check for bundled installer in the bot folder first
set TESS_INSTALLER=
for %%F in ("%~dp0tesseract-ocr-w64-setup*.exe") do set TESS_INSTALLER=%%F

if defined TESS_INSTALLER (
    echo  [~] Found bundled Tesseract installer: !TESS_INSTALLER!
    echo  [~] Installing Tesseract silently...
    "!TESS_INSTALLER!" /S
    timeout /t 15 /nobreak >nul
    goto :tesseract_check
)

:: No bundled installer - download it
echo  [~] Downloading Tesseract OCR...
curl -L --progress-bar -o "%TEMP%\tesseract_installer.exe" https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe
if errorlevel 1 (
    echo  [!] Download failed. Install manually:
    echo      https://github.com/UB-Mannheim/tesseract/wiki
    goto :tesseract_done
)
echo  [~] Installing Tesseract silently...
"%TEMP%\tesseract_installer.exe" /S
timeout /t 15 /nobreak >nul

:tesseract_check
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo  [OK] Tesseract installed successfully.
    goto :tesseract_done
)

echo  [!] Silent install failed - launching manual installer...
echo      IMPORTANT: Keep the default install path^!
if defined TESS_INSTALLER (
    "!TESS_INSTALLER!"
) else (
    "%TEMP%\tesseract_installer.exe"
)

if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo  [OK] Tesseract installed.
) else (
    echo  [!] Tesseract still not found. Please install manually:
    echo      https://github.com/UB-Mannheim/tesseract/wiki
)

:tesseract_done

:: ── Check / Install ADB ───────────────────────────────────────
echo.
echo  [6/6] Checking ADB...

if exist "%~dp0adb.exe" (
    echo  [OK] adb.exe already in bot folder.
    goto :adb_done
)

adb --version >nul 2>&1
if not errorlevel 1 (
    echo  [OK] ADB found in system PATH.
    goto :adb_done
)

echo  [~] Downloading ADB platform-tools...
curl -L --progress-bar -o "%TEMP%\platform-tools.zip" https://dl.google.com/android/repository/platform-tools-latest-windows.zip
if errorlevel 1 (
    echo  [!] ADB download failed. Add adb.exe manually to the bot folder.
    goto :adb_done
)

echo  [~] Extracting ADB...
powershell -Command "Expand-Archive -Path '%TEMP%\platform-tools.zip' -DestinationPath '%TEMP%\pt-extract' -Force" >nul 2>&1
copy "%TEMP%\pt-extract\platform-tools\adb.exe"          "%~dp0adb.exe"          >nul 2>&1
copy "%TEMP%\pt-extract\platform-tools\AdbWinApi.dll"    "%~dp0AdbWinApi.dll"    >nul 2>&1
copy "%TEMP%\pt-extract\platform-tools\AdbWinUsbApi.dll" "%~dp0AdbWinUsbApi.dll" >nul 2>&1

if exist "%~dp0adb.exe" (
    echo  [OK] ADB extracted to bot folder.
) else (
    echo  [!] ADB extraction failed. Add adb.exe manually.
)

:adb_done

:: ── Create shortcuts ──────────────────────────────────────────
echo.
echo  Creating shortcuts...

(
    echo @echo off
    echo title COC Bot - THE KRAKEN
    echo cd /d "%%~dp0"
    echo python app.py %%*
    echo if errorlevel 1 pause
    echo pause
) > "%~dp0run.bat"

(
    echo @echo off
    echo title COC Bot - Reconfigure
    echo cd /d "%%~dp0"
    echo python app.py --reconfigure
    echo pause
) > "%~dp0reconfigure.bat"

echo  [OK] run.bat and reconfigure.bat created.

:: ── Verify everything ────────────────────────────────────────
echo.
echo  Verifying installation...

%PYTHON_CMD% -c "import cv2, numpy, PIL, pytesseract; print('  [OK] All Python packages working')"
if errorlevel 1 (
    echo  [!] One or more packages failed. Try: pip install -r requirements.txt
)

if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo  [OK] Tesseract found at C:\Program Files\Tesseract-OCR\
) else if exist "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe" (
    echo  [OK] Tesseract found at C:\Program Files (x86)\Tesseract-OCR\
) else (
    echo  [!] Tesseract not found - please install it manually:
    echo      https://github.com/UB-Mannheim/tesseract/wiki
)

if exist "%~dp0adb.exe" (
    echo  [OK] adb.exe present in bot folder.
) else (
    echo  [!] adb.exe missing from bot folder.
)

:: ── Done ─────────────────────────────────────────────────────
echo.
echo  ============================================================
echo    INSTALLATION COMPLETE!
echo  ============================================================
echo.
echo  Before starting the bot:
echo    1. Open LDPlayer
echo    2. Settings - Other settings - Enable ADB on port 5555
echo    3. Open Clash of Clans - go to main village screen
echo.
echo  Then double-click run.bat to start the bot.
echo.
pause