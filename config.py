"""
Configuration for the AR Hand Panel application.
"""

# CAMERA
CAMERA_INDEX: int = 0
CAMERA_WIDTH: int = 1280
CAMERA_HEIGHT: int = 720
CAMERA_FLIP: bool = True

# HAND TRACKING
MP_MAX_HANDS: int = 2
MP_DETECTION_CONFIDENCE: float = 0.45  # Lower threshold = much easier to detect hands initially
MP_TRACKING_CONFIDENCE: float = 0.45   # Lower threshold = maintains tracking much better when hands move fast

# SMOOTHING
SMOOTH_ALPHA: float = 0.35
SMOOTH_MIN_ALPHA: float = 0.05       # Lower value = ultra smooth when hands are still
SMOOTH_MAX_ALPHA: float = 0.95       # Higher value = zero lag when hands are moving fast
SMOOTH_VELOCITY_SCALE: float = 0.08  # Tuned for pixel-space coordinates (flushes noise, zero motion lag)

# PANEL
PANEL_ASPECT_RATIO: float = 16.0 / 10.0
PANEL_BORDER_THICKNESS: int = 4
PANEL_BORDER_COLOR = (255, 255, 255)

# EFFECTS
HALFTONE_CELL_SIZE: int = 8
HALFTONE_COLOR = (45, 35, 190)        # Red in BGR
POSTERIZE_LEVELS: int = 4
NOISE_STRENGTH: float = 25.0
