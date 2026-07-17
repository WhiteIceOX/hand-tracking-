# AR Hand Panel — Miles Morales & Pop-Art Interactive Shaders

Aplikasi Augmented Reality (AR) interaktif berbasis **OpenGL** dan **MediaPipe Hand Landmarker** yang melacak pergerakan jari tangan secara real-time dan menggambar panel seni visual pop-art serta gaya estetika komik *Spider-Man: Into the Spider-Verse*.

---

## 🚀 Fitur Utama

1. **Gaya Visual Spider-Verse & Pop-Art (10 Filter Keren)**:
   * **Mode 0**: Risograph Red Halftone (Gaya cetak retro merah krim).
   * **Mode 1**: Blue Blueprint Drawing Grid (Cetakan biru arsitek).
   * **Mode 2**: Green Digital Matrix (Scanline terminal hacker hijau).
   * **Mode 3**: **Spider-Verse CMYK Ben-Day Dots** (Titik komik + warna cetak bergeser).
   * **Mode 4**: **Miles Morales Glitch** (Khusus warna Merah, Biru, dan Hitam Tinta).
   * **Mode 5**: **Spider-Verse Cel Shading** (Flat toon shading Miles Morales + shimmer biru).
   * **Mode 6**: Manga Ink Sketch (Arsiran sketsa hitam-putih).
   * **Mode 7**: **Spider-Verse Glitch Dimension Portal** (Sobekan warna dimensi & sobekan layar).
   * **Mode 8**: **Vibrant Anime Cel-Shading** (Warna saturasi tinggi + kilau Sakura Pink).
   * **Mode 9**: **Vintage Dark Comic Ink** (Arsiran tinta hitam-merah pekat komik klasik).

2. **AI-Style Motion Predictor (Anti-Kedip/Dropout)**:
   * Memakai estimasi fisika kecepatan konstan (*Constant Velocity Model*) dan peredam momentum (*friction decay*) untuk memproyeksikan pergerakan jari selama maksimal 15 frame ketika terhalang/gelap. Tracking menjadi sangat mulus dan tidak mudah hilang.

3. **Transition Glitch Effect**:
   * Setiap kali filter berganti, panel akan mengalami visual glitch selama 0,25 detik berupa getaran fisik bidang, robekan piksel digital (*screen tearing*), pemisahan warna (*chromatic aberration*), dan border yang berkedip neon.

4. **Zero-Latency Audio Feedback**:
   * Memutar berkas suara `mixkit-retro-arcade-casino-notification-211.wav` secara instan langsung dari memori RAM (tanpa jeda disk I/O) saat filter berganti.

---

## 🎮 Skema Kontrol

### 1. Kontrol Tampilan Panel (Keyboard)
* **Tombol `P`**: Mengganti jumlah panel aktif secara berurutan:
  * **1 Panel** (Default): Hanya melacak & menggambar Kotak 1 (**Jempol + Telunjuk**).
  * **2 Panel**: Melacak & menggambar Kotak 1 + Kotak 2 (**Telunjuk + Jari Tengah**).
  * **3 Panel**: Melacak & menggambar Kotak 1 + Kotak 2 + Kotak 3 (**Jari Tengah + Kelingking**).

### 2. Kontrol Pergantian Filter
* **Dalam Mode 1 atau 2 Panel**:
  * **Cukup ketuk/sentuhkan ujung jari** Anda untuk mengganti filter panel secara instan (tanpa menekan tombol keyboard).
    * Ketuk **Jempol & Telunjuk** -> Mengganti filter Panel 0.
    * Ketuk **Telunjuk & Jari Tengah** -> Mengganti filter Panel 1.
* **Dalam Mode 3 Panel (Seluruh Jari)**:
  * Ketukan jari dinonaktifkan agar tidak sengaja terpicu.
  * **Tekan tombol `M`** pada keyboard untuk mengganti filter seluruh panel secara bersamaan.

### 3. Kontrol Sistem Lainnya
* **Tombol `F`**: Mengaktifkan / menonaktifkan mode layar penuh (Fullscreen).
* **Tombol `Q` / `ESC`**: Menutup aplikasi secara aman.

---

## 📦 Prasyarat & Instalasi

Pastikan Anda telah menginstal Python 3.10 ke atas pada Windows Anda.

1. Buka Command Prompt (cmd) di folder ini, lalu pasang dependensi berikut:
   ```bash
   pip install numpy opencv-python mediapipe PyOpenGL glfw
   ```

2. Unduh berkas model MediaPipe:
   * Program akan mengunduh model secara otomatis saat pertama kali dijalankan dan menyimpannya di folder `assets/hand_landmarker.task`.

---

## 🏃‍♂️ Cara Menjalankan

* **Windows (Cara Cepat)**:
  * Cukup klik dua kali berkas **`run.bat`** di folder project.
* **Command Line**:
  * Jalankan perintah berikut di terminal/cmd:
    ```bash
    python main.py
    ```
