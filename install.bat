@echo off
cls
title Book Alchemist Intelligent Installer

echo #################################################################
echo #                                                               #
echo #           Welcome to the Book Alchemist Installer             #
echo #                                                               #
echo #################################################################
echo.

:: === Step 1: Choose Installation Mode ===
:choose_mode
cls
echo Please choose your desired setup mode:
echo.
echo   [1] API Key Mode (Lightweight & Recommended for most users)
echo       - Requires an internet connection to use the AI.
echo       - You will use your own API key (OpenAI or Perplexity).
echo       - Very small and fast installation.
echo.
echo   [2] Local AI Mode (Full Offline Installation)
echo       - Runs 100%% offline and privately on your computer.
echo       - Requires a powerful computer with an NVIDIA GPU (4GB+ VRAM).
echo       - Very large download and setup (several GBs).
echo.
set /p choice="Enter your choice (1 or 2): "
if "%choice%"=="1" goto api_setup
if "%choice%"=="2" goto local_setup
echo Invalid choice. Please press Enter to try again.
pause >nul
goto choose_mode

:: === API Setup Branch ===
:api_setup
set REQUIREMENTS_FILE=requirements_api.txt
set INSTALL_MODE=API
goto check_python

:: === Local AI Setup Branch ===
:local_setup
set REQUIREMENTS_FILE=requirements_local.txt
set INSTALL_MODE=Local
goto check_python

:: === Step 2: Check for Python (or Install It) ===
:check_python
cls
echo [Step 1/5] Checking for Python...
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo Python is already installed and in the PATH.
    goto create_venv
)

echo Python not found. This script will now attempt to download and install it automatically.
echo This is required for the application to run.
echo.
pause
echo Downloading Python 3.11 (64-bit)...
powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe -OutFile python-installer.exe"
if %errorlevel% neq 0 (
    echo ERROR: Failed to download Python installer. Please check your internet connection and try again.
    pause
    exit /b
)

echo Installing Python silently. Your screen may flash for security approval...
start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
del python-installer.exe

cls
echo ############################# ACTION REQUIRED ##############################
echo.
echo Python has been installed.
echo.
echo For the system to recognize the new installation, you must
echo close this window and RE-RUN the 'install.bat' script.
echo.
echo ############################################################################
echo.
pause
exit /b

:: === Step 3: Create Virtual Environment ===
:create_venv
cls
echo [Step 2/5] Setting up virtual environment...
if not exist venv (
    echo Creating new virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)
echo.

:: === Step 4: Install Dependencies ===
:install_deps
cls
echo [Step 3/5] Installing Python packages for %INSTALL_MODE% mode...
echo This may take a few minutes.
call venv\Scripts\pip.exe install -r %REQUIREMENTS_FILE%
if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages. Please check your internet connection.
    pause
    exit /b
)

if "%INSTALL_MODE%"=="Local" (
    echo.
    echo Installing PyTorch for NVIDIA GPU... (This is a large download)
    call venv\Scripts\pip.exe install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    
    echo.
    echo Installing Llama.cpp for local AI... (Using pre-compiled version for Python 3.11)
    call venv\Scripts\pip.exe install https://github.com/jllllll/llama-cpp-python-cuBLAS-wheels/releases/download/cpu-only/llama_cpp_python-0.2.77-cp311-cp311-win_amd64.whl
)
echo.

:: === Step 5: Install Playwright Browsers ===
:install_playwright
cls
echo [Step 4/5] Installing browser for PDF generation...
call venv\Scripts\playwright.exe install
echo.

:: === Step 6: Final Setup Steps ===
:final_steps
cls
echo [Step 5/5] Final setup...
if "%INSTALL_MODE%"=="Local" (
    if not exist models\mistral-7b-instruct-v0.2.q4_k_m.gguf (
        echo.
        echo ############################# ACTION REQUIRED ##############################
        echo.
        echo The final step is to download the AI model file.
        echo.
        echo 1. Open this URL in your browser:
        echo    https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
        echo.
        echo 2. Find and download the file: mistral-7b-instruct-v0.2.q4_k_m.gguf (~4.37 GB)
        echo.
        echo 3. Create a folder named 'models' in your project directory.
        echo.
        echo 4. Place the downloaded '.gguf' file inside the 'models' folder.
        echo.
        echo ############################################################################
        echo.
        echo Press Enter after you have downloaded and placed the model file correctly.
        pause
    ) else (
        echo AI model file already found.
    )
) else (
    echo.
    echo Reminder: To use the AI, open the app, go to Settings,
    echo and enter your API key for OpenAI or Perplexity.
    echo.
)
cls

:end_script
echo.
echo =================================================================
echo.
echo                  INSTALLATION COMPLETE!
echo.
echo =================================================================
echo.
echo You can now run the application by double-clicking the 'run_app.bat' file.
echo.
pause