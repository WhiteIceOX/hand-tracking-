"""
Adaptive smoothing for hand landmarks.
"""
import numpy as np


class AdaptiveSmoother:
    """Smooths a 2D/3D point stream using velocity-adaptive exponential filtering."""

    def __init__(self, alpha: float = 0.35, min_alpha: float = 0.15,
                 max_alpha: float = 0.75, velocity_scale: float = 8.0):
        self._base_alpha = alpha
        self._min_alpha = min_alpha
        self._max_alpha = max_alpha
        self._velocity_scale = velocity_scale
        self._value = None
        self._prev_raw = None

    def update(self, raw: np.ndarray) -> np.ndarray:
        raw = np.asarray(raw, dtype=np.float64)
        if self._value is None:
            self._value = raw.copy()
            self._prev_raw = raw.copy()
            return self._value.copy()

        velocity = np.linalg.norm(raw - self._prev_raw)
        self._prev_raw = raw.copy()

        # Fast movement → higher alpha (more responsive)
        # Slow movement → lower alpha (more smooth)
        t = min(velocity * self._velocity_scale, 1.0)
        alpha = self._min_alpha + t * (self._max_alpha - self._min_alpha)

        self._value = alpha * raw + (1.0 - alpha) * self._value
        return self._value.copy()

    def reset(self):
        self._value = None
        self._prev_raw = None


class LandmarkSmoother:
    """Manages adaptive smoothers for each landmark of each hand."""

    def __init__(self, num_landmarks: int = 21, **kwargs):
        self._num_landmarks = num_landmarks
        self._kwargs = kwargs
        # {hand_label: [AdaptiveSmoother for each landmark]}
        self._smoothers: dict[str, list[AdaptiveSmoother]] = {}

    def smooth(self, hand_label: str, landmarks: list[tuple[float, float]], width: float, height: float) -> list[tuple[float, float]]:
        if hand_label not in self._smoothers:
            self._smoothers[hand_label] = [
                AdaptiveSmoother(**self._kwargs) for _ in range(self._num_landmarks)
            ]

        smoothed = []
        for i, (x, y) in enumerate(landmarks):
            if i < len(self._smoothers[hand_label]):
                # Convert to pixel space
                pixel_x = x * width
                pixel_y = y * height
                
                # Update smoother in pixel coordinates
                pt = self._smoothers[hand_label][i].update(np.array([pixel_x, pixel_y]))
                
                # Convert back to normalized space [0.0, 1.0]
                smoothed.append((pt[0] / width, pt[1] / height))
            else:
                smoothed.append((x, y))

        return smoothed

    def remove_hand(self, hand_label: str):
        if hand_label in self._smoothers:
            del self._smoothers[hand_label]

    def reset(self):
        self._smoothers.clear()


class HandPredictor:
    """Predicts hand motion and bridges short tracking dropouts using a velocity model."""

    def __init__(self, max_missing_frames: int = 15):
        self.max_missing_frames = max_missing_frames
        # {hand_label: {"landmarks": list, "velocity": list, "missing_frames": int, "hand_data": HandData}}
        self.states = {}

    def update(self, detected_hands: list, width: float, height: float) -> list:
        from tracker import HandData
        seen_labels = set()

        for hand in detected_hands:
            label = hand.label
            seen_labels.add(label)

            if label in self.states:
                prev_lm = self.states[label]["landmarks"]
                # Compute velocity in pixel space
                vels = []
                for curr, prev in zip(hand.landmarks, prev_lm):
                    vx = (curr[0] - prev[0]) * width
                    vy = (curr[1] - prev[1]) * height
                    vels.append((vx, vy))

                # Smooth the velocity vector (EMA)
                prev_vels = self.states[label]["velocity"]
                smooth_vels = []
                for v_curr, v_prev in zip(vels, prev_vels):
                    vx = 0.4 * v_curr[0] + 0.6 * v_prev[0]
                    vy = 0.4 * v_curr[1] + 0.6 * v_prev[1]
                    smooth_vels.append((vx, vy))

                self.states[label] = {
                    "landmarks": hand.landmarks,
                    "velocity": smooth_vels,
                    "missing_frames": 0,
                    "hand_data": hand
                }
            else:
                # Initialize state with zero velocity
                vels = [(0.0, 0.0) for _ in range(21)]
                self.states[label] = {
                    "landmarks": hand.landmarks,
                    "velocity": vels,
                    "missing_frames": 0,
                    "hand_data": hand
                }

        # Predict coordinates for missing hands
        for label in list(self.states.keys()):
            if label not in seen_labels:
                self.states[label]["missing_frames"] += 1
                if self.states[label]["missing_frames"] > self.max_missing_frames:
                    # Timeout exceeded, drop the hand state
                    del self.states[label]
                else:
                    prev_lm = self.states[label]["landmarks"]
                    vels = self.states[label]["velocity"]
                    pred_lm = []

                    # Project coordinates forward
                    for pt, v in zip(prev_lm, vels):
                        nx = pt[0] + v[0] / width
                        ny = pt[1] + v[1] / height
                        pred_lm.append((nx, ny))

                    # Apply momentum decay (friction) to prevent infinite drift
                    decay_vels = [(v[0] * 0.9, v[1] * 0.9) for v in vels]

                    # Re-calculate pinch point
                    pinch_pt = ((pred_lm[4][0] + pred_lm[8][0]) / 2.0,
                                (pred_lm[4][1] + pred_lm[8][1]) / 2.0)

                    old_hand = self.states[label]["hand_data"]
                    pred_hand = HandData(
                        label=label,
                        landmarks=pred_lm,
                        pinch_point=pinch_pt,
                        is_pinching=old_hand.is_pinching
                    )

                    self.states[label]["landmarks"] = pred_lm
                    self.states[label]["velocity"] = decay_vels
                    self.states[label]["hand_data"] = pred_hand

        return [state["hand_data"] for state in self.states.values()]
