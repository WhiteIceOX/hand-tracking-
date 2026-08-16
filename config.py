"""
Configuration for the AR Hand Panel application.

Panduan konfigurasi untuk pengguna pemula:
- Jika kamera tidak terdeteksi, coba ganti CAMERA_INDEX ke 1 atau 2
- Jika aplikasi terasa lambat, ganti CAMERA_WIDTH/HEIGHT ke 640x480
- Jika tangan sulit terdeteksi, turunkan nilai MP_DETECTION_CONFIDENCE ke 0.3
"""

# ─── KAMERA ───────────────────────────────────────────────────────────────────
# Index kamera: 0 = kamera pertama (built-in), 1 = kamera kedua (eksternal), dst.
CAMERA_INDEX: int = 0

# Resolusi input kamera. Ganti ke 640x480 jika laptop lambat.
CAMERA_WIDTH: int = 1280
CAMERA_HEIGHT: int = 720

# Flip horizontal (True = mirror seperti selfie, False = tidak di-flip)
CAMERA_FLIP: bool = True

# ─── HAND TRACKING ────────────────────────────────────────────────────────────
# Jumlah tangan yang dideteksi (maksimal 2)
MP_MAX_HANDS: int = 2

# Nilai 0.0 - 1.0. Lebih rendah = lebih mudah terdeteksi, tapi lebih banyak false positive
MP_DETECTION_CONFIDENCE: float = 0.45
MP_TRACKING_CONFIDENCE: float = 0.45

# ─── SMOOTHING ────────────────────────────────────────────────────────────────
# Kontrol kelembutan gerakan panel (tidak perlu diubah untuk pengguna biasa)
SMOOTH_ALPHA: float = 0.35
SMOOTH_MIN_ALPHA: float = 0.05   # Makin rendah = makin halus saat diam
SMOOTH_MAX_ALPHA: float = 0.95   # Makin tinggi = makin responsif saat bergerak cepat
SMOOTH_VELOCITY_SCALE: float = 0.08

# ─── PANEL ────────────────────────────────────────────────────────────────────
PANEL_ASPECT_RATIO: float = 16.0 / 10.0
PANEL_BORDER_THICKNESS: int = 4
PANEL_BORDER_COLOR = (255, 255, 255)

# ─── EFEK VISUAL ──────────────────────────────────────────────────────────────
HALFTONE_CELL_SIZE: int = 8
HALFTONE_COLOR = (45, 35, 190)   # Warna dalam format BGR
POSTERIZE_LEVELS: int = 4
NOISE_STRENGTH: float = 25.0
