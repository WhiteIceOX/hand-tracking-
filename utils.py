"""
Utility functions: logging, model download, FPS counter.
"""
import logging
import os
import time
import urllib.request
import ssl


MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
MODEL_PATH = os.path.join("assets", "hand_landmarker.task")


def setup_logging(level=logging.INFO):
    fmt = "%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
    logging.basicConfig(level=level, format=fmt, datefmt="%H:%M:%S")
    return logging.getLogger("Main")


def download_hand_landmarker_model() -> str:
    """Download the MediaPipe HandLandmarker model if not present."""
    if os.path.isfile(MODEL_PATH):
        return MODEL_PATH

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    logger = logging.getLogger("ModelDL")
    logger.info(f"Downloading hand_landmarker.task model (~5.6 MB)...")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH, context=ctx)
        logger.info("Model downloaded successfully!")
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        raise

    return MODEL_PATH


class FPSCounter:
    """Simple FPS counter using a rolling window."""

    def __init__(self, window_size: int = 30):
        self._window_size = window_size
        self._timestamps: list[float] = []

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


import os
import winsound

# Preload the audio file into memory once at startup to eliminate disk I/O latency
_WAV_DATA = None
try:
    _dir_path = os.path.dirname(os.path.abspath(__file__))
    _wav_path = os.path.join(_dir_path, "mixkit-retro-arcade-casino-notification-211.wav")
    if os.path.exists(_wav_path):
        with open(_wav_path, "rb") as _f:
            _WAV_DATA = _f.read()
except Exception:
    _WAV_DATA = None


def play_transition_sound():
    """Play the preloaded WAV sound effect instantly from memory with zero disk/thread overhead."""
    global _WAV_DATA
    try:
        if _WAV_DATA is not None:
            # Play instantly from memory. SND_ASYNC automatically cuts off previous sound.
            winsound.PlaySound(_WAV_DATA, winsound.SND_MEMORY | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        else:
            # Asynchronous fallback to synthesized beep sequence if WAV is missing
            import threading
            def _beep():
                try:
                    winsound.Beep(988, 40)
                    winsound.Beep(1480, 50)
                except Exception:
                    pass
            threading.Thread(target=_beep, daemon=True).start()
    except Exception:
        pass


def play_tap_sound():
    """Play the transition sound for finger tap filter changes."""
    play_transition_sound()


def play_keyboard_sound():
    """Play the transition sound for keyboard filter changes."""
    play_transition_sound()
