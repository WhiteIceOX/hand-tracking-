# 🚨 Panduan Solusi Error & Troubleshooting

Jika Anda atau teman Anda mengalami kendala saat menginstall atau menjalankan aplikasi **AR Hand Panel**, temukan kasus error Anda di bawah ini dan ikuti solusinya dengan mudah! 🛠️✨

---

## 🔴 Kasus 1: File `run.bat` Terbuka Lalu Langsung Tertutup Sendiri (Flash Crash) ⚡
* **❓ Penyebab:** Terjadi error pada Python, dan jendela otomatis menutup cepat sebelum pesan error sempat terbaca.
* **💡 Solusi (Cara Melihat Pesan Error Asli):**
  1. 📂 Buka folder project Anda di File Explorer.
  2. 🔍 Klik pada kolom alamat folder di bagian atas (*Address Bar*).
  3. ⌨️ Ketik **`cmd`** lalu tekan **Enter**.
  4. 💻 Di jendela hitam yang muncul, ketik:
     ```bash
     python main.py
     ```
  5. 👁️ Tekan **Enter**. Sekarang jendela tidak akan tertutup dan pesan error aslinya akan terlihat jelas di layar!

---

## 🔴 Kasus 2: `ERROR: Could not find a version that satisfies the requirement mediapipe` 🐍
* **❓ Penyebab:**
  1. Laptop Anda terpasang Python versi **32-bit** (MediaPipe hanya ada untuk versi 64-bit).
  2. Laptop Anda memakai Python versi yang terlalu baru (misalnya Python 3.13+ yang belum didukung MediaPipe).
* **💡 Solusi:**
  1. 🗑️ Buka *Windows Settings* $\rightarrow$ *Apps* $\rightarrow$ *Installed Apps*, lalu **Uninstall (Hapus)** semua Python yang ada.
  2. 📥 Download dan pasang **[Python 3.10 64-bit Resmi](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)**.
  3. ⚠️ **Jangan lupa centang:** `[x] Add Python 3.10 to PATH` saat memasang ulang!

---

## 🔴 Kasus 3: `'pip'` atau `'python'` is not recognized as an internal or external command ⚙️
* **❓ Penyebab:** Kotak *Add to PATH* terlewat/lupa dicentang saat menginstal Python.
* **💡 Solusi:**
  * 🔄 Buka file installer Python lagi, pilih opsi **Modify**, lalu centang opsi **Add Python to Environment Variables / PATH**.
  * ⌨️ **ATAU** gunakan perintah bawaan ini di Command Prompt (CMD):
    ```bash
    py -m pip install numpy opencv-python mediapipe PyOpenGL glfw
    ```

---

## 🔴 Kasus 4: Kamera Tidak Mau Menyala / Layar Gelap (*Failed to open camera*) 📷
* **❓ Penyebab:** Izin akses kamera diblokir oleh sistem Windows atau webcam sedang dipakai aplikasi lain.
* **💡 Solusi:**
  1. ❌ Tutup aplikasi yang memakai kamera (Zoom, Microsoft Teams, Google Meet, OBS, Discord, atau aplikasi Camera).
  2. ⚙️ Buka **Windows Settings** $\rightarrow$ **Privacy & Security** $\rightarrow$ **Camera**.
  3. 🟢 Pastikan tombol **Camera access** bernilai **ON**.
  4. 🟢 Pastikan tombol **Let desktop apps access your camera** bernilai **ON**.
  5. 🔍 Periksa apakah laptop Anda memiliki penutup kamera fisik (*slider shutter*) yang masih tertutup.

---

## 🔴 Kasus 5: Error OpenGL / Layar Putih Blank / `Failed to initialize OpenGL renderer` 🖥️
* **❓ Penyebab:** Driver kartu grafis (VGA) laptop belum terupdate atau laptop menggunakan GPU hemat daya yang belum mendukung standar OpenGL 3.3 Core Profile.
* **💡 Solusi:**
  1. 🚀 Update driver VGA laptop Anda (Intel HD Graphics, NVIDIA, atau AMD Radeon).
  2. 🎮 **Untuk laptop Dual GPU (Intel + NVIDIA):**
     * Klik kanan pada Desktop $\rightarrow$ pilih **NVIDIA Control Panel**.
     * Masuk ke menu **Manage 3D Settings** $\rightarrow$ tab **Program Settings**.
     * Tambahkan `python.exe` lalu ubah pilihan GPU ke **High-performance NVIDIA processor**.
     * Klik **Apply**.

---

## 🔴 Kasus 6: Muncul Pesan Error `MSVCP140.dll` atau `VCRUNTIME140.dll is missing` 🧩
* **❓ Penyebab:** Laptop kekurangan paket runtime Microsoft C++.
* **💡 Solusi:**
  1. 📥 Download dan install: **[Visual C++ Redistributable 2015-2022 (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe)**.
  2. 🔄 Restart laptop Anda.

---

> 🔙 *Kembali ke panduan utama:* **[`README.md`](README.md)** | *Panduan instalasi:* **[`INSTALLATION.md`](INSTALLATION.md)** ✨
