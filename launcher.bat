@echo off
setlocal enabledelayedexpansion

title Game Suite Launcher (Final Fixed)
cls
echo ===================================
echo  Game Suite Launcher
echo ===================================
echo Searching for a valid Python environment...
echo.

:: ------------------------------------------------------------------
:: Define base paths dynamically to make the script portable.
:: %~dp0 expands to the drive and path of the current script.
:: ------------------------------------------------------------------
set "GAME_DIR=%~dp0"
:: Trim the trailing backslash from the path for cleaner concatenation.
set "GAME_DIR=%GAME_DIR:~0,-1%"

:: Define paths for potential environments.
set "DATA_SUITE_ACTIVATE=%GAME_DIR%\..\data_suite\Scripts\activate.bat"
set "EMBED_PYTHON="
for /d %%G in ("%GAME_DIR%\python_embed\python-*") do set "EMBED_PYTHON=%%G\python.exe"

:: ------------------------------------------------------------------
:: Main Logic - Attempt to launch using different methods in order.
:: ------------------------------------------------------------------

:: Priority 1: data_suite (Special handling for compound command)
echo [1] Checking for 'data_suite' environment...
if exist "%DATA_SUITE_ACTIVATE%" (
    echo     -^> Found data_suite. Verifying packages...
    call "%DATA_SUITE_ACTIVATE%" && python -c "import tkinter" >nul 2>nul
    if !errorlevel! == 0 (
        echo     -^> Success. Launching application...
        echo -----------------------------------
        cd /d "%GAME_DIR%"
        call "%DATA_SUITE_ACTIVATE%" && python main.py
        goto :End
    ) else (
        setlocal disabledelayedexpansion
        echo     -^> [!] Package check failed for data_suite.
        endlocal
    )
)

:: Priority 2: Embedded
echo [2] Checking for embedded Python...
if defined EMBED_PYTHON if exist "%EMBED_PYTHON%" (
    call :_verifyAndLaunch "Embedded" """%EMBED_PYTHON%"""
    if !errorlevel! == 0 goto :End
)

:: Priority 3: System Path
echo [3] Checking for system Python...
where python >nul 2>nul
if %errorlevel! == 0 (
    call :_verifyAndLaunch "System" "python"
    if !errorlevel! == 0 goto :End
)

:: If all checks have failed, show error.
goto :AllFailed

:: ------------------------------------------------------------------
:: VERIFY & LAUNCH SUBROUTINE (For simple executable paths)
:: Returns errorlevel 0 on successful run, 1 on package failure.
:: %1 = Environment Name (e.g., "Embedded")
:: %2 = Python Command (e.g., """C:\path\to\python.exe""")
:: ------------------------------------------------------------------
:_verifyAndLaunch
    echo     -^> Found %~1. Verifying packages...
    %~2 -c "import tkinter" >nul 2>nul
    if !errorlevel! == 0 (
        echo     -^> Success. Launching application...
        echo -----------------------------------
        cd /d "%GAME_DIR%"
        %~2 main.py
        :: App ran successfully, return success code 0.
        exit /b 0
    ) else (
        setlocal disabledelayedexpansion
        echo     -^> [!] Package check failed for %~1.
        endlocal
        :: Package check failed, return failure code 1.
        exit /b 1
    )

:: ------------------------------------------------------------------
:: Final exit points
:: ------------------------------------------------------------------
:AllFailed
echo.
echo [X] ERROR: Could not find a complete Python environment.
echo Please ensure an environment with Tkinter is available.

:End
echo.
echo -----------------------------------
echo The program has closed.
echo Press any key to exit.
pause >nul
endlocal

