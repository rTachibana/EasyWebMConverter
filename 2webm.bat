@echo off
chcp 65001 > nul
echo 2webm - MP4 to WebM Encoder
echo ===========================

rem Check directory and run setup
set NEEDS_SETUP=0

if not exist "%~dp0python\python.exe" (
    echo Python not found. Setup required.
    set NEEDS_SETUP=1
)

if not exist "%~dp0ffmpeg\bin\ffmpeg.exe" (
    echo FFmpeg not found. Setup required.
    set NEEDS_SETUP=1
)

if "%NEEDS_SETUP%"=="1" (
    echo Running automatic setup...
    echo This may take a few minutes. Please wait...
    echo.
    call "%~dp0setup.bat"
    
    rem Check for existence again after setup
    set SETUP_FAILED=0
    if not exist "%~dp0python\python.exe" set SETUP_FAILED=1
    if not exist "%~dp0ffmpeg\bin\ffmpeg.exe" set SETUP_FAILED=1
    
    if "%SETUP_FAILED%"=="1" (
        echo.
        echo Setup failed to install required components.
        echo Please try running setup.bat manually.
        pause
        exit /b 1
    )
    
    echo.
    echo Setup completed successfully.
    echo.
)

rem Launch the application
echo Launching application...
"%~dp0python\python.exe" "%~dp0src\main.py"

rem If there was an error
if %errorlevel% neq 0 (
    echo Failed to start the application.
    echo Run setup.bat to reinstall.
    pause
) 