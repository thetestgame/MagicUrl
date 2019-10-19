@echo off
title AWS Web - Update Serverless
cd ../
goto :INPUT

rem Request user input
:INPUT
    set ENVIRONMENT=dev
    set /P ENVIRONMENT=Environment (dev [Default], test, prod):
    goto :TAIL

rem Run Tail
:TAIL
    zappa %ENVIRONMENT% tail

    pause
    goto :EOF