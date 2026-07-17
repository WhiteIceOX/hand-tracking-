"""
Hand tracking using MediaPipe Tasks API (HandLandmarker).
Extracts hand landmarks and pinch points for panel placement.
"""
import logging
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)

logger = logging.getLogger("Tracker")


# MediaPipe hand landmark indices
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
WRIST = 0
INDEX_MCP = 5
PINKY_MCP = 17


class HandData:
    """Stores processed data for a single detected hand."""

    def __init__(self, label: str, landmarks: list[tuple[float, float]],
                 pinch_point: tuple[float, float], is_pinching: bool):
        self.label = label                  # "Left" or "Right"
        self.landmarks = landmarks          # All 21 landmarks (normalized 0-1)
        self.pinch_point = pinch_point      # Midpoint of thumb tip and index tip
        self.is_pinching = is_pinching      # Whether thumb and index are close

    @property
    def thumb_tip(self) -> tuple[float, float]:
        return self.landmarks[THUMB_TIP]

    @property
    def index_tip(self) -> tuple[float, float]:
        return self.landmarks[INDEX_TIP]

    @property
    def wrist(self) -> tuple[float, float]:
        return self.landmarks[WRIST]


class HandTracker:
    """MediaPipe HandLandmarker wrapper using Tasks API."""

    def __init__(self, model_path: str, max_hands: int = 2,
                 detection_confidence: float = 0.7,
                 tracking_confidence: float = 0.7):
        self._model_path = model_path
        self._max_hands = max_hands
        self._detection_confidence = detection_confidence
        self._tracking_confidence = tracking_confidence
        self._landmarker = None
        self._frame_count = 0

    def start(self):
        """Initialize the HandLandmarker."""
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self._model_path),
            running_mode=RunningMode.VIDEO,
            num_hands=self._max_hands,
            min_hand_detection_confidence=self._detection_confidence,
            min_hand_presence_confidence=self._detection_confidence,
            min_tracking_confidence=self._tracking_confidence,
        )
        self._landmarker = HandLandmarker.create_from_options(options)
        logger.info("HandLandmarker initialized (Tasks API).")

    def process_frame(self, frame_bgr: np.ndarray) -> list[HandData]:
        """Process a BGR frame and return list of HandData."""
        if self._landmarker is None:
            return []

        self._frame_count += 1
        timestamp_ms = int(self._frame_count * (1000 / 30))

        # Downscale image to 320x180 to filter out sensor noise and speed up CPU detection dramatically
        h, w = frame_bgr.shape[:2]
        target_w = 320
        target_h = int(h * (target_w / w))
        small_bgr = cv2.resize(frame_bgr, (target_w, target_h), interpolation=cv2.INTER_AREA)

        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(small_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        try:
            result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        except Exception as e:
            logger.warning(f"Detection error: {e}")
            return []

        hands = []
        if result.hand_landmarks and result.handedness:
            for i, (landmarks, handedness) in enumerate(
                zip(result.hand_landmarks, result.handedness)
            ):
                # Get hand label — flip for mirror view
                raw_label = handedness[0].category_name
                label = "Right" if raw_label == "Left" else "Left"

                # Extract normalized landmarks
                lm_list = [(lm.x, lm.y) for lm in landmarks]

                # Compute pinch point and distance
                thumb = np.array(lm_list[THUMB_TIP])
                index = np.array(lm_list[INDEX_TIP])
                pinch_point = tuple((thumb + index) / 2.0)
                pinch_dist = np.linalg.norm(thumb - index)
                is_pinching = pinch_dist < 0.06

                hands.append(HandData(
                    label=label,
                    landmarks=lm_list,
                    pinch_point=pinch_point,
                    is_pinching=is_pinching,
                ))

        return hands

    def stop(self):
        """Release the landmarker."""
        if self._landmarker:
            self._landmarker.close()
            self._landmarker = None
            logger.info("HandLandmarker released.")
