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

:: ─── Cari Python Windows yang valid (skip MSYS2/Conda) ────────────────────
set "PYTHON_EXE="

:: Prioritas 1: Cari di lokasi standar instalasi Python Windows (AppData)
for %%D in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Python\bin\python.exe"
) do (
    if exist %%D (
        set "PYTHON_EXE=%%~D"
        goto :python_found
    )
)

:: Prioritas 2: Cari di C:\PythonXX dan Program Files
for %%D in (
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Program Files\Python313\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python310\python.exe"
) do (
    if exist %%D (
        set "PYTHON_EXE=%%~D"
        goto :python_found
    )
)

:: Prioritas 3: Cari "python" dari PATH, tapi skip MSYS2/MinGW/Conda
for /f "tokens=*" %%P in ('where python 2^>nul') do (
    echo %%P | findstr /I "msys mingw cygwin conda" >nul
    if !ERRORLEVEL! neq 0 (
        set "PYTHON_EXE=%%P"
        goto :python_found
    )
)

:: Tidak ditemukan
echo  [ERROR] Python tidak ditemukan di komputer ini!
echo.
echo  Silakan install Python terlebih dahulu:
echo  1. Buka: https://www.python.org/downloads/
echo  2. Download Python 3.11 (64-bit) - REKOMENDASI
echo  3. PENTING: Centang "Add Python to PATH" saat instalasi!
echo  4. Restart komputer, lalu jalankan file ini lagi.
echo.
pause
exit /b 1

:python_found
echo  [OK] Python ditemukan: %PYTHON_EXE%
for /f "tokens=2 delims= " %%V in ('"%PYTHON_EXE%" --version 2^>^&1') do (
    echo  [OK] Versi Python: %%V
)
echo.

:: ─── Setup Virtual Environment ──────────────────────────────────────────────
:: Gunakan %~dp0 langsung (sudah include trailing backslash)

if exist "%~dp0venv\Scripts\python.exe" (
    echo  [OK] Virtual environment sudah ada.
    goto :install_deps
)

echo  [INFO] Membuat virtual environment (hanya sekali)...
"%PYTHON_EXE%" -m venv "%~dp0venv"
if %ERRORLEVEL% neq 0 (
    echo.
    echo  [ERROR] Gagal membuat virtual environment!
    echo  Coba install ulang Python dari python.org
    echo.
    pause
    exit /b 1
)

if not exist "%~dp0venv\Scripts\python.exe" (
    echo.
    echo  [ERROR] Virtual environment gagal dibuat.
    echo  Pastikan menggunakan Python dari python.org
    echo.
    pause
    exit /b 1
)
echo  [OK] Virtual environment berhasil dibuat.

:install_deps
:: Cek apakah library sudah terinstall
"%~dp0venv\Scripts\python.exe" -c "import mediapipe, cv2, glfw, OpenGL, numpy" >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo  [OK] Semua library sudah siap.
    goto :run_app
)

echo  [INFO] Menginstall library yang diperlukan...
echo  [INFO] Proses ini mungkin butuh 2-5 menit, harap tunggu...
echo.

"%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
"%~dp0venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"

if %ERRORLEVEL% neq 0 (
    echo.
    echo  [ERROR] Gagal menginstall library!
    echo  Pastikan koneksi internet aktif dan coba lagi.
    echo  Atau buka TROUBLESHOOTING.md untuk bantuan.
    echo.
    pause
    exit /b 1
)

echo.
echo  [OK] Semua library berhasil diinstall!

:run_app
:: ─── Jalankan aplikasi ──────────────────────────────────────────────────────
echo.
echo  [INFO] Memulai AR Hand Panel...
echo  [INFO] Tekan Q atau Escape untuk keluar dari aplikasi.
echo.
"%~dp0venv\Scripts\python.exe" "%~dp0main.py"

:: ─── Error handler ───────────────────────────────────────────────────────────
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
