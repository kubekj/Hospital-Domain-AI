@REM The Client "called" needs to output a fixed solution or similar instantly
@REM then the bat script opens maximizes the MAvis server and takes a screenshot of it

@echo off
setlocal enabledelayedexpansion

@REM set "JAR_PATH=server.jar"
@REM set "PYTHON_SCRIPT_PATH=python searchclient_python\searchclient\searchclient.py"
@REM set "NIRCMD_PATH=nircmd.exe"
@REM set "SCREENSHOT_SAVE_PATH=complevels\images"
@REM set "LEVELS_PATH=complevels"

set "STEPS_TO_ROOT=..\..\"
set "JAR_PATH=%STEPS_TO_ROOT%server.jar"
set "PYTHON_SCRIPT_PATH=py %STEPS_TO_ROOT%src\searches\graphsearch.py"
set "NIRCMD_PATH=nircmd.exe"
set "SCREENSHOT_SAVE_PATH=%STEPS_TO_ROOT%complevels2024\images"
set "LEVELS_PATH=%STEPS_TO_ROOT%complevels2024"
@REM set "LEVELS_PATH=%STEPS_TO_ROOT%levels\custom"

for %%F in ("!LEVELS_PATH!\*.lvl") do (
    set "LEVEL=%%F"
    set "FILENAME=%%~nF"
    set CMD=start "" java -jar "!JAR_PATH!" -l "!LEVEL!" -c "!PYTHON_SCRIPT_PATH!" -g -s 150 -t 180
    echo Running command: !CMD! on !LEVEL!
    !CMD!
    
    echo Waiting for the application to initialize...
    timeout /t 3 /nobreak >nul

    echo Maximizing the application window...
    !NIRCMD_PATH! win max title "MAvis"
    
    timeout /t 2 /nobreak >nul

    call :captureScreenshot "MAvis" "!FILENAME!"
    
    echo Closing the application...
    call :closeApplication "MAvis"
    timeout /t 3 /nobreak >nul
)
goto :eof

:captureScreenshot
set "WINDOW_TITLE=%~1"
set "FILENAME=%~2"
echo Attempting to capture: !FILENAME!
!NIRCMD_PATH! savescreenshotwin "!SCREENSHOT_SAVE_PATH!\!FILENAME!.png" title "!WINDOW_TITLE!"
goto :eof

:closeApplication
set "WINDOW_TITLE=%~1"
echo Attempting to close: !WINDOW_TITLE!
!NIRCMD_PATH! win close title "!WINDOW_TITLE!"
goto :eof
