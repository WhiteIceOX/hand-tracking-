"""
Utility functions: logging, model download, audio, FPS counter.
"""
import logging
import os
import sys
import time
import urllib.request
import ssl
import glob


# ─── Model Download ──────────────────────────────────────────────────────────
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"

# Path relatif ke direktori script ini sendiri (bukan CWD)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(_SCRIPT_DIR, "assets", "hand_landmarker.task")


def setup_logging(level=logging.INFO):
    fmt = "%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
    logging.basicConfig(level=level, format=fmt, datefmt="%H:%M:%S")
    return logging.getLogger("Main")


def _show_progress(block_num, block_size, total_size):
    """Callback untuk menampilkan progress download di console."""
    if total_size > 0:
        downloaded = block_num * block_size
        percent = min(100, downloaded * 100 // total_size)
        bar = "=" * (percent // 5) + " " * (20 - percent // 5)
        sys.stdout.write(f"\r  Download: [{bar}] {percent}%  ")
        sys.stdout.flush()
        if percent >= 100:
            print()


def download_hand_landmarker_model(max_retries: int = 3) -> str:
    """Download the MediaPipe HandLandmarker model if not present, with retry."""
    if os.path.isfile(MODEL_PATH):
        return MODEL_PATH

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    logger = logging.getLogger("ModelDL")
    logger.info("Downloading hand_landmarker.task model (~5.6 MB)...")
    print("\n  [INFO] Model hand tracking belum ada. Mendownload sekarang (~5.6 MB)...")
    print("  [INFO] Pastikan koneksi internet aktif!\n")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for attempt in range(1, max_retries + 1):
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH, reporthook=_show_progress)
            logger.info("Model downloaded successfully!")
            print("  [OK] Model berhasil didownload!\n")
            return MODEL_PATH
        except Exception as e:
            logger.warning(f"Download attempt {attempt}/{max_retries} failed: {e}")
            # Hapus file yang mungkin rusak
            if os.path.exists(MODEL_PATH):
                os.remove(MODEL_PATH)
            if attempt < max_retries:
                print(f"  [RETRY] Percobaan {attempt} gagal. Mencoba lagi ({attempt+1}/{max_retries})...")
                time.sleep(2)
            else:
                logger.error("All download attempts failed.")
                print("\n  [ERROR] Gagal mendownload model setelah beberapa percobaan.")
                print("  Periksa koneksi internet dan coba lagi.\n")
                raise RuntimeError(
                    "Gagal mendownload model MediaPipe. Cek koneksi internet lalu coba lagi."
                ) from e


# ─── FPS Counter ─────────────────────────────────────────────────────────────
class FPSCounter:
    """Simple FPS counter using a rolling window."""

    def __init__(self, window_size: int = 30):
        self._window_size = window_size
        self._timestamps: list = []

    def tick(self) -> float:
        now = time.perf_counter()
        self._timestamps.append(now)
        if len(self._timestamps) > self._window_size:
            self._timestamps.pop(0)
        if len(self._timestamps) < 2:
            return 0.0
        elapsed = self._timestamps[-1] - self._timestamps[0]
        if elapsed <= 0:
            return 0.0
        return (len(self._timestamps) - 1) / elapsed


# ─── Audio Playback ───────────────────────────────────────────────────────────
# Preload audio dari folder assets (cari file .wav manapun)
_WAV_DATA = None

def _find_wav_in_assets() -> str | None:
    """Cari file .wav pertama di folder assets, relatif ke script."""
    assets_dir = os.path.join(_SCRIPT_DIR, "assets")
    wav_files = glob.glob(os.path.join(assets_dir, "*.wav"))
    if wav_files:
        return wav_files[0]
    # Cari juga di direktori utama (root project)
    root_wavs = glob.glob(os.path.join(_SCRIPT_DIR, "*.wav"))
    if root_wavs:
        return root_wavs[0]
    return None


def _load_audio():
    """Load WAV file ke memory (preloading untuk zero-latency playback)."""
    global _WAV_DATA
    wav_path = _find_wav_in_assets()
    if wav_path and os.path.exists(wav_path):
        try:
            with open(wav_path, "rb") as f:
                _WAV_DATA = f.read()
            logging.getLogger("Audio").info(f"Audio preloaded: {os.path.basename(wav_path)}")
        except Exception as e:
            logging.getLogger("Audio").warning(f"Could not preload audio: {e}")
            _WAV_DATA = None
    else:
        logging.getLogger("Audio").info("No WAV file found in assets/. Using beep fallback.")
        _WAV_DATA = None


# Jalankan loading audio saat modul diimport
_load_audio()


def _play_beep_fallback():
    """Fallback beep jika tidak ada file WAV (Windows only, tanpa crash)."""
    import threading
    def _beep():
        try:
            import winsound
            winsound.Beep(988, 40)
            winsound.Beep(1480, 50)
        except Exception:
            pass
    threading.Thread(target=_beep, daemon=True).start()


def play_transition_sound():
    """Play sound effect dari memory dengan zero disk latency."""
    global _WAV_DATA
    try:
        if _WAV_DATA is not None:
            import winsound
            winsound.PlaySound(
                _WAV_DATA,
                winsound.SND_MEMORY | winsound.SND_ASYNC | winsound.SND_NODEFAULT
            )
        else:
            _play_beep_fallback()
    except ImportError:
        # Bukan Windows — abaikan saja
        pass
    except Exception:
        pass


def play_tap_sound():
    """Play sound untuk finger tap filter change."""
    play_transition_sound()


def play_keyboard_sound():
    """Play sound untuk keyboard filter change."""
    play_transition_sound()
