@echo off
title Running AR Hand Panel...
cd /d "D:\KULIAH\semester 2\tetst dulu\hand tracking 2"
echo Starting AR Hand Panel (60 FPS)...
"C:\Users\ASUS\AppData\Local\Python\bin\python.exe" main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Application crashed or exited with error code %ERRORLEVEL%.
    pause
)
