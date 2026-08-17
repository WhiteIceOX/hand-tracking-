# 🕷️  Hand Tracking  ✨

Aplikasi **Augmented Reality (AR)** interaktif berbasis **OpenGL** dan **MediaPipe AI Hand Landmarker** yang melacak pergerakan jari tangan secara real-time dan memproyeksikan panel seni visual pop-art serta estetika komik *Spider-Man: Into the Spider-Verse* langsung di antara ujung jari Anda! 🎨🚀

---

## 📚 Daftar Panduan & Dokumentasi
* 🛠️ **[Panduan Instalasi Lengkap (INSTALLATION.md)](INSTALLATION.md)** — Langkah pasang Python 64-bit, Visual C++, dan library untuk semua laptop.
* 🚨 **[Panduan Solusi Error (TROUBLESHOOTING.md)](TROUBLESHOOTING.md)** — Solusi lengkap jika terjadi crash `run.bat`, kamera tidak muncul, atau modul hilang.

---

## 🚀 Fitur-Fitur Utama Project

### 🎨 1. 10 Gaya Visual Shaders Unik (GLSL)
Aplikasi ini dilengkapi dengan 10 shader visual kustom yang dapat diganti secara interaktif dan instan:

* 🔴 **Mode 0: Risograph Red Halftone** — Gaya cetak seni retro merah-krim dengan tekstur titik halftone 45°.
* 🔵 **Mode 1: Blue Blueprint Drawing Grid** — Garis kisi-kisi arsitektur biru elektrik (*cyan duotone*).
* 🟢 **Mode 2: Green Digital Matrix** — Efek terminal hacker hijau neon dengan scanline digital bergerak.
* 🕷️ **Mode 3: Spider-Verse CMYK Ben-Day Dots** — Cetakan komik vintage otentik dengan titik Ben-Day berjarak tetap dan efek pergeseran warna percetakan (*CMYK mis-registration*).
* ⚡ **Mode 4: Miles Morales Glitch (Red, Blue & Black)** — Palet khas Miles Morales dengan pemisahan warna merah & biru neon pada latar hitam tinta pekat, dilengkapi *slice-tearing* dinamis.
* 🕸️ **Mode 5: Spider-Verse Cel Shading** — *Toon shading* 4-level flat color Miles Morales dengan aksen shimmer biru *web-shooter*.
* 🖋️ **Mode 6: Manga Ink Sketch** — Arsiran tangan sketsa hitam-putih (*cross-hatching ink*).
* 🌌 **Mode 7: Spider-Verse Glitch Dimension Portal** — Efek sobekan portal antar-dimensi dengan *chromatic aberration* berputar dan Ben-Day dots Magenta/Cyan bergantian.
* 🌸 **Mode 8: Vibrant Anime Cel-Shading** — Warna saturasi tinggi (1.6x boost) dengan *lighting cel-shading*, kilau pastel Sakura Pink, dan inking hitam anime.
* 📜 **Mode 9: Vintage Dark Comic Ink** — Kertas komik tua kusam dengan bayangan 3 tingkat hitam pekat, merah gelap, dan merah komik klasik.

---

### 🧠 2. AI-Style Motion Predictor (Anti-Kedip & Anti-Dropout)
* **Masalah Umum:** Kamera webcam sering kehilangan deteksi tangan saat jari saling menindih (*self-occlusion*), bergerak cepat, atau dalam pencahayaan redup.
* **Solusi Pintar:** Menggunakan algoritma **Constant Velocity Model** dengan redaman gesekan (*friction decay* 10%). Sistem secara cerdas **memprediksi arah dan kecepatan gerak 21 sendi jari** hingga 15 frame ke depan saat deteksi terputus, sehingga panel tidak hilang, tidak berkedip (*no flicker*), dan langsung tersambung mulus saat tangan kembali terdeteksi! 🛡️🖐️

---

### 💥 3. Transition Glitch Effect (Spider-Verse Style)
Setiap kali filter berganti, panel aktif akan mengalami efek visual transisi glitch selama **0,25 detik**:
* 📳 **Physical Quad Shake:** Bidang panel 3D bergetar secara fisik di layar melalui pergeseran koordinat acak (*coordinate jitter*).
* 🌈 **Chromatic Aberration:** Gambar kamera membelah menjadi bayangan warna Cyan & Magenta di tepi objek.
* ⚡ **Digital Screen Tearing:** Distorsi gelombang dan efek sobek horizontal frekuensi tinggi.
* 💡 **Border Color Flickering:** Garis tepi berkedip berganti antara warna asli dan warna neon dimensi.

---

### 🔊 4. Zero-Latency Audio Feedback (RAM Preloading)
* Efek suara transisi (`mixkit-retro-arcade-casino-notification-211.wav`) langsung dimuat ke dalam memori RAM saat program pertama kali dibuka.
* Suara diputar seketika (*0ms latency*) saat jari diketuk tanpa hambatan baca hard disk (Disk I/O). ⚡🎵

---

## 🎮 Skema Kontrol Lengkap

### 1. 🎛️ Kontrol Tampilan Panel (Keyboard)
* **Tombol `P`**: Mengganti jumlah panel aktif secara berurutan:
  * **1 Panel (Default):** Hanya melacak & menggambar Kotak 1 (**Jempol + Telunjuk**).
  * **2 Panel:** Melacak & menggambar Kotak 1 + Kotak 2 (**Telunjuk + Jari Tengah**).
  * **3 Panel:** Melacak & menggambar Kotak 1 + Kotak 2 + Kotak 3 (**Jari Tengah + Kelingking**).

### 2. 🖐️ Kontrol Pergantian Filter
* **Dalam Mode 1 atau 2 Panel:**
  * **Cukup ketuk/sentuhkan ujung jari** Anda untuk mengganti filter panel secara instan (tanpa menekan keyboard):
    * 👆 Ketuk **Jempol & Telunjuk** $\rightarrow$ Mengganti filter Panel 0.
    * ✌️ Ketuk **Telunjuk & Jari Tengah** $\rightarrow$ Mengganti filter Panel 1.
* **Dalam Mode 3 Panel (Seluruh Jari):**
  * Ketukan jari dinonaktifkan agar tidak sengaja terpicu saat tangan terbuka lebar.
  * ⌨️ **Tekan tombol `M`** pada keyboard untuk mengganti filter seluruh panel secara bersamaan.

### 3. 🖥️ Kontrol Tambahan
* **Tombol `F`**: Layar penuh (*Fullscreen* on/off). 🔲
* **Tombol `ESC` / `Q`**: Menutup aplikasi secara aman. 🚪

---

## 🏃‍♂️ Cara Menjalankan Aplikasi

1. 📂 Buka folder project ini di komputer Anda.
2. 🖱️ **Klik 2x pada file `run.bat`**.
3. 🎉 Aplikasi akan otomatis menyala dan siap dimainkan!

> ⚠️ **Pertama kali install:** `run.bat` akan otomatis mendownload semua library yang dibutuhkan. Pastikan koneksi internet aktif dan tunggu hingga selesai (2–5 menit).

---

## 🛡️ Jika `run.bat` Diblokir Windows (SmartScreen)

Beberapa laptop Windows 11 memblokir file `.bat` yang baru didownload. Ini **normal** dan bukan virus. Ikuti salah satu cara berikut:

### Cara 1 — Unblock via Properties (Paling Mudah)
1. Klik kanan file `run.bat`
2. Pilih **Properties**
3. Di bagian bawah, centang **"Unblock"** ✅
4. Klik **OK**
5. Klik 2x `run.bat` seperti biasa

### Cara 2 — Jalankan sebagai Administrator
1. Klik kanan file `run.bat`
2. Pilih **"Run as administrator"**
3. Klik **Yes** jika muncul popup konfirmasi

### Cara 3 — Lewat Command Prompt
1. Tekan `Win + R`, ketik `cmd`, tekan Enter
2. Ketik perintah berikut lalu tekan Enter:
   ```
   cd /d "PATH_FOLDER_PROJECT"
   run.bat
   ```

---

> 💡 *Butuh panduan instalasi dari nol? Buka:* **[`INSTALLATION.md`](INSTALLATION.md)** 🛠️  
> 💡 *Aplikasi error / tidak bisa terbuka? Buka:* **[`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)** 🚨
