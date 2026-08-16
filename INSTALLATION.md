# 🛠️ Panduan Lengkap Instalasi (Untuk Semua Laptop)

Panduan praktis, mudah dipahami, dan ramah pemula untuk memasang seluruh kebutuhan aplikasi **AR Hand Panel** di laptop/komputer Windows Anda. ✨

---

## 📋 Langkah 1: Download & Pasang Python yang Tepat (Wajib 64-Bit) 🐍

> ⚠️ **PENTING BANGET:** Modul AI `mediapipe` **HANYA BISA** berjalan di Python versi **64-bit** (bukan 32-bit) dan versi **Python 3.10 atau 3.11**.

1. 📥 **Download Installer Resmi:**
   * Klik link resmi berikut: **[Download Python 3.10.11 (Windows 64-bit)](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)**
2. 🖱️ **Buka File Installer yang Sudah Didownload:**
   * ⚠️ **WAJIB CENTANG** kotak di bagian paling bawah:
     > `[x] Add Python 3.10 to PATH`
   * Klik tombol **"Install Now"** di bagian atas.
3. 🎉 **Selesai:**
   * Jika di akhir instalasi muncul tombol bertuliskan *Disable path length limit*, klik tombol tersebut lalu klik **Close**.

---

## 🧱 Langkah 2: Pasang Microsoft Visual C++ (Pencegah Error DLL) ⚙️

Banyak laptop Windows (terutama laptop baru) belum memiliki paket C++ bawaan yang dibutuhkan oleh OpenCV & OpenGL.

1. 📥 **Download File Resmi Microsoft:**
   * Klik link resmi berikut: **[Visual C++ Redistributable 2015-2022 (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe)**
2. 🖱️ Buka filenya, centang persetujuan, lalu klik **Install / Repair**.
3. 🔄 Restart laptop jika diminta.

---

## 📦 Langkah 3: Install Library Tambahan (Cukup 1 Baris Perintah) 💻

1. ⌨️ Tekan tombol **`Windows + R`** di keyboard laptop Anda.
2. 📝 Ketik **`cmd`** lalu tekan **Enter** (Jendela hitam Command Prompt akan terbuka).
3. 📋 Salin dan tempel perintah ini satu per satu lalu tekan **Enter**:

   ```bash
   python -m pip install --upgrade pip
   ```
   ```bash
   pip install numpy opencv-python mediapipe PyOpenGL glfw
   ```

4. ⏳ Tunggu proses download selesai sampai muncul pesan hijau/sukses (*Successfully installed...*).

---

## 🚀 Langkah 4: Cara Menjalankan Program 🎮

* 🟢 **Cara Paling Mudah (Sekali Klik):**
  * Buka folder project ini di komputer Anda.
  * **Klik 2x pada file `run.bat`**.
* 🟡 **Cara Manual Lewat Command Prompt (CMD):**
  ```bash
  python main.py
  ```

---

## ✅ Checklist Sebelum Bermain ✨
- [x] Laptop terhubung dengan kamera / webcam.
- [x] Tidak ada aplikasi lain yang sedang memakai webcam (Zoom/Meet/Teams sudah ditutup).
- [x] Pencahayaan ruangan cukup terang agar jari mudah terdeteksi.

> 💡 *Jika menemukan kendala atau error saat instalasi/menjalankan program, buka file panduan:* **[`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)**! 🚨
