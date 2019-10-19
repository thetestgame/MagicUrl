@echo off
title AWS Web - Unit Tests
cd ../

rem Upload Assets
:main 
    echo Activating environment.
    CALL "env/Scripts/activate.bat"

    echo Starting upload.
    python -m tests

    echo Complete
    pause