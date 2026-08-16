@echo off
setlocal EnableDelayedExpansion
title AR Hand Panel - Memulai...
cd /d "%~dp0"

echo.
echo  ============================================
echo    AR Hand Panel - Pop-Art Edition
echo    Sistem Visual Tangan dengan OpenGL
echo  ============================================
echo.

:: ─── Cari Python secara otomatis ───────────────────────────────────────────
set PYTHON_CMD=

:: Cek "python" dulu
python --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON_CMD=python
    goto :python_found
)

:: Cek "python3"
python3 --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON_CMD=python3
    goto :python_found
)

:: Cek "py" (Windows Launcher)
py --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON_CMD=py
    goto :python_found
)

:: Python tidak ditemukan
echo  [ERROR] Python tidak ditemukan di komputer ini!
echo.
echo  Silakan install Python terlebih dahulu:
echo  1. Buka: https://www.python.org/downloads/
echo  2. Download Python 3.10 atau 3.11 (64-bit)
echo  3. PENTING: Centang "Add Python to PATH" saat instalasi!
echo  4. Restart komputer, lalu jalankan file ini lagi.
echo.
pause
exit /b 1

:python_found
echo  [OK] Python ditemukan: %PYTHON_CMD%

:: ─── Cek versi Python (minimal 3.10) ───────────────────────────────────────
for /f "tokens=2 delims= " %%V in ('%PYTHON_CMD% --version 2^>^&1') do set PY_VER=%%V
echo  [OK] Versi Python: %PY_VER%

:: ─── Install / cek dependencies ────────────────────────────────────────────
echo.
echo  [INFO] Memeriksa dependencies...
%PYTHON_CMD% -c "import mediapipe, cv2, glfw, OpenGL, numpy" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo  [INFO] Beberapa library belum terinstall. Menginstall sekarang...
    echo  [INFO] Harap tunggu, proses ini mungkin butuh beberapa menit...
    echo.
    %PYTHON_CMD% -m pip install --upgrade pip --quiet
    %PYTHON_CMD% -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo.
        echo  [ERROR] Gagal menginstall dependencies!
        echo  Coba jalankan perintah ini secara manual di Command Prompt:
        echo     pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo.
    echo  [OK] Semua library berhasil diinstall!
) else (
    echo  [OK] Semua library sudah terinstall.
)

:: ─── Jalankan aplikasi ─────────────────────────────────────────────────────
echo.
echo  [INFO] Memulai AR Hand Panel...
echo  [INFO] Tekan Q atau Escape untuk keluar dari aplikasi.
echo.
%PYTHON_CMD% main.py

:: ─── Tangani error saat keluar ─────────────────────────────────────────────
if %ERRORLEVEL% neq 0 (
    echo.
    echo  ============================================
    echo   Aplikasi keluar dengan error (kode: %ERRORLEVEL%)
    echo  ============================================
    echo.
    echo  Kemungkinan penyebab:
    echo  - Kamera tidak terdeteksi (coba cabut dan pasang kembali)
    echo  - Driver GPU tidak mendukung OpenGL 3.3
    echo  - Library belum terinstall dengan benar
    echo.
    echo  Buka TROUBLESHOOTING.md untuk panduan lengkap.
    echo.
    pause
)
endlocal
