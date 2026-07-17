"""
Main Application for the Pop-Art AR Hand Panel.
Coordinates the camera, tracker, and OpenGL rendering thread.
Computes the 3D tetrahedron geometry between two hands and renders
it at 60 FPS.
"""
import sys
import time
import logging
import threading
import numpy as np
import cv2
import glfw
from OpenGL.GL import *

import config
import utils
from tracker import HandTracker, HandData
from smoothing import LandmarkSmoother
from renderer import OpenGLRenderer

# Setup logging
logger = utils.setup_logging()


FINGER_TO_MODE = {
    8: 0,   # Index -> Red Halftone
    12: 1,  # Middle -> Blue Blueprint
    16: 2,  # Ring -> Green Matrix
    20: 3   # Pinky -> Pink Pop-Art
}

# Global active shader modes for the 3 panels
panel_modes = [0, 1, 2]
active_panels_count = 1  # 1: Thumb-Index, 2: Adds Index-Middle, 3: Adds Middle-Pinky
last_cycle_time = [0.0, 0.0, 0.0]  # Timestamps of the last filter cycle per panel for transition glitch


def count_extended_fingers(landmarks):
    # landmarks: list of 21 points [x, y]
    # Y coordinate is 0 at top and 1 at bottom.
    extended = 0
    
    # 1. Index finger (landmark 8 tip vs 6 PIP joint)
    if landmarks[8][1] < landmarks[6][1]:
        extended += 1
    # 2. Middle finger (landmark 12 tip vs 10 PIP joint)
    if landmarks[12][1] < landmarks[10][1]:
        extended += 1
    # 3. Ring finger (landmark 16 tip vs 14 PIP joint)
    if landmarks[16][1] < landmarks[14][1]:
        extended += 1
    # 4. Pinky finger (landmark 20 tip vs 18 PIP joint)
    if landmarks[20][1] < landmarks[18][1]:
        extended += 1
        
    # 5. Thumb (check distance from thumb tip to index base MCP vs overall palm size)
    thumb_tip = np.array(landmarks[4])
    mcp_index = np.array(landmarks[5])
    mcp_pinky = np.array(landmarks[17])
    palm_size = np.linalg.norm(mcp_index - mcp_pinky)
    
    if np.linalg.norm(thumb_tip - mcp_index) > palm_size * 0.7:
        extended += 1
        
    return extended


class ThreadedCamera:
    """Captures frames from the webcam in a background thread to prevent blocking."""

    def __init__(self, index: int, width: int, height: int):
        self.index = index
        self.width = width
        self.height = height
        self.cap = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        self.thread = None

    def start(self) -> bool:
        self.cap = cv2.VideoCapture(self.index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        if not self.cap.isOpened():
            return False

        # Get actual resolution
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.running = True
        self.thread = threading.Thread(target=self._update, name="camera-capture", daemon=True)
        self.thread.start()
        return True

    def _update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                with self.lock:
                    self.frame = frame
            else:
                time.sleep(0.005)

    def get_frame(self) -> np.ndarray | None:
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()


class ThreadedTracker:
    """Processes hand tracking in a background thread to maintain high rendering frame rate."""

    def __init__(self, tracker_inst: HandTracker):
        self.tracker = tracker_inst
        self.frame = None
        self.hands = []
        self.running = False
        self.lock = threading.Lock()
        self.event = threading.Event()
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._update, name="hand-tracking", daemon=True)
        self.thread.start()

    def update_frame(self, frame: np.ndarray):
        with self.lock:
            self.frame = frame.copy()
        self.event.set()

    def _update(self):
        while self.running:
            self.event.wait()
            self.event.clear()

            with self.lock:
                if self.frame is None:
                    continue
                frame_to_process = self.frame.copy()

            hands = self.tracker.process_frame(frame_to_process)
            
            with self.lock:
                self.hands = hands

    def get_hands(self) -> list[HandData]:
        with self.lock:
            return list(self.hands)

    def stop(self):
        self.running = False
        self.event.set()
        if self.thread:
            self.thread.join(timeout=1.0)


def key_callback(window, key, scancode, action, mods):
    global panel_modes
    global active_panels_count
    global last_cycle_time
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_F:
            # Toggle fullscreen
            is_fullscreen = glfw.get_window_monitor(window) is not None
            if is_fullscreen:
                glfw.set_window_monitor(window, None, 100, 100, 1280, 720, 0)
            else:
                monitor = glfw.get_primary_monitor()
                mode = glfw.get_video_mode(monitor)
                glfw.set_window_monitor(window, monitor, 0, 0, mode.width, mode.height, mode.refresh_rate)
        elif key == glfw.KEY_P:
            active_panels_count = active_panels_count + 1
            if active_panels_count > 3:
                active_panels_count = 1
            
            # Trigger glitch transition on all panels when configuration changes
            import time
            curr_t = time.perf_counter()
            for i in range(3):
                last_cycle_time[i] = curr_t
                
            # Play the transition sound when changing layout configuration
            utils.play_keyboard_sound()
            logger.info(f"Keyboard panels configuration: active panels count set to {active_panels_count}")
        elif key == glfw.KEY_M:
            if active_panels_count == 3:
                panel_modes[0] = (panel_modes[0] + 1) % 10
                panel_modes[1] = (panel_modes[1] + 1) % 10
                panel_modes[2] = (panel_modes[2] + 1) % 10
                
                # Trigger glitch transition on all panels when cycling filters
                import time
                curr_t = time.perf_counter()
                for i in range(3):
                    last_cycle_time[i] = curr_t
                    
                # Play the transition sound when cycling filters in 3-panel mode
                utils.play_keyboard_sound()
                logger.info(f"Keyboard cycle (Key M): All panels cycled to modes: {panel_modes}")
            else:
                logger.info(f"Keyboard cycle (Key M) ignored: only active when displaying 3 panels (currently: {active_panels_count})")


def main():
    logger.info("Initializing AR Hand Panel (Pop-Art Style)...")

    # Download model if not exists
    model_path = utils.download_hand_landmarker_model()

    # Create hardware interfaces
    camera = ThreadedCamera(config.CAMERA_INDEX, config.CAMERA_WIDTH, config.CAMERA_HEIGHT)
    if not camera.start():
        logger.critical("Failed to open camera!")
        sys.exit(1)

    logger.info(f"Camera started with resolution: {camera.width}x{camera.height}")

    # Initialize tracker
    raw_tracker = HandTracker(
        model_path=model_path,
        max_hands=config.MP_MAX_HANDS,
        detection_confidence=config.MP_DETECTION_CONFIDENCE,
        tracking_confidence=config.MP_TRACKING_CONFIDENCE,
    )
    raw_tracker.start()
    
    tracker = ThreadedTracker(raw_tracker)
    tracker.start()

    # Initialize landmark smoother and prediction model
    from smoothing import LandmarkSmoother, HandPredictor
    
    smoother = LandmarkSmoother(
        num_landmarks=21,
        alpha=config.SMOOTH_ALPHA,
        min_alpha=config.SMOOTH_MIN_ALPHA,
        max_alpha=config.SMOOTH_MAX_ALPHA,
        velocity_scale=config.SMOOTH_VELOCITY_SCALE,
    )
    
    predictor = HandPredictor(max_missing_frames=15)

    # Initialize renderer
    renderer = OpenGLRenderer(camera.width, camera.height, "AR Hand Panel - Pop-Art (60 FPS)")
    if not renderer.initialize():
        logger.critical("Failed to initialize OpenGL renderer!")
        camera.stop()
        tracker.stop()
        raw_tracker.stop()
        sys.exit(1)

    glfw.set_key_callback(renderer.window, key_callback)

    fps_counter = utils.FPSCounter()
    start_time = time.perf_counter()
    last_panels_data = {0: None, 1: None, 2: None}
    lost_frames = 0
    lost_frames_limit = 20

    # Dynamic tap-to-cycle filter controls
    # 3 pairs per hand: [Thumb-Index, Index-Middle, Middle-Pinky]
    last_tap_states = {
        "Left": [False, False, False],
        "Right": [False, False, False]
    }
    global panel_modes  # Use the global panel_modes shared with key_callback
    global active_panels_count  # Use the global active_panels_count shared with key_callback
    global last_cycle_time  # Use the global last_cycle_time shared with key_callback
    active_hands_last_frame = set()

    def check_finger_contacts(landmarks):
        lm = [np.array(p) for p in landmarks]
        # Pair 0: Thumb (4) and Index (8)
        contact_0 = np.linalg.norm(lm[4] - lm[8]) < 0.065
        # Pair 1: Index (8) and Middle (12)
        contact_1 = np.linalg.norm(lm[8] - lm[12]) < 0.055
        # Pair 2: Middle (12) and Pinky (20)
        contact_2 = np.linalg.norm(lm[12] - lm[20]) < 0.075
        return [contact_0, contact_1, contact_2]

    while not glfw.window_should_close(renderer.window):
        current_time = time.perf_counter()
        t_val = current_time - start_time

        # Get latest frame
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.001)
            continue

        if config.CAMERA_FLIP:
            frame = cv2.flip(frame, 1)

        # Update tracker frame
        tracker.update_frame(frame)

        # Get tracked hands
        hands = tracker.get_hands()

        # Apply smoothing to detected hands
        smoothed_hands = []
        for hand in hands:
            smoothed_lm = smoother.smooth(hand.label, hand.landmarks, float(camera.width), float(camera.height))
            pinch_pt = ((smoothed_lm[4][0] + smoothed_lm[8][0]) / 2.0,
                        (smoothed_lm[4][1] + smoothed_lm[8][1]) / 2.0)
            smoothed_hands.append(HandData(
                label=hand.label,
                landmarks=smoothed_lm,
                pinch_point=pinch_pt,
                is_pinching=hand.is_pinching
            ))

        # Use AI-like motion prediction to bridge short tracking dropouts
        active_hands = predictor.update(smoothed_hands, float(camera.width), float(camera.height))

        # Reset smoother and tap states only for hands that are truly lost (timed out in predictor)
        active_labels = {hand.label for hand in active_hands}
        for label in ["Left", "Right"]:
            if label not in active_labels:
                smoother.remove_hand(label)
                last_tap_states[label] = [False, False, False]

        # Check for both hands to draw panels
        left_hand = None
        right_hand = None
        for hand in active_hands:
            if hand.label == "Left":
                left_hand = hand
            elif hand.label == "Right":
                right_hand = hand

        # Check finger tap transitions to cycle modes on either hand
        for hand in active_hands:
            label = hand.label
            current_contacts = check_finger_contacts(hand.landmarks)
            
            # Only detect transitions if the hand was already tracked in the previous frame
            if label in active_hands_last_frame:
                prev_contacts = last_tap_states[label]
                for idx in range(3):
                    # Rising edge: contact just made
                    if current_contacts[idx] and not prev_contacts[idx]:
                        # Only cycle via tap if we are NOT in 3-panel mode (1 or 2 panels active) and the panel is visible
                        if active_panels_count < 3 and idx < active_panels_count:
                            panel_modes[idx] = (panel_modes[idx] + 1) % 10
                            last_cycle_time[idx] = time.perf_counter()
                            utils.play_tap_sound()
                            logger.info(f"Panel {idx} mode cycled to {panel_modes[idx]} via {label} hand tap.")
            
            last_tap_states[label] = current_contacts

        panels_to_render = []

        if left_hand is not None and right_hand is not None:
            lm_L = left_hand.landmarks
            lm_R = right_hand.landmarks

            # Determine how many panels to enable based on active_panels_count (controlled by key P)
            max_panels = active_panels_count

            # 3 Panels configurations: (top_landmark_id, bottom_landmark_id, panel_index)
            panel_configs = [
                (8, 4, 0),   # Kotak 1: Index & Thumb
                (12, 8, 1),  # Kotak 2: Middle & Index
                (20, 12, 2)  # Kotak 3: Pinky & Middle
            ]

            # Clear cache for any modes that are not drawn this frame (so they don't persist on release)
            for idx, (_, _, panel_idx) in enumerate(panel_configs):
                if idx >= max_panels:
                    last_panels_data[panel_idx] = None

            for idx, (top_id, bottom_id, panel_idx) in enumerate(panel_configs[:max_panels]):
                mode = panel_modes[panel_idx]

                # Calculate glitch factor (lasts 0.25 seconds)
                elapsed = current_time - last_cycle_time[panel_idx]
                glitch_factor = max(0.0, 1.0 - elapsed / 0.25)

                # Physical screen shaking displacement
                jx, jy = 0.0, 0.0
                if glitch_factor > 0.0:
                    import random
                    # Shake displacement up to 0.03 normalized screen coordinates
                    jx = random.uniform(-0.03, 0.03) * glitch_factor
                    jy = random.uniform(-0.03, 0.03) * glitch_factor

                # Left hand (TL and BL)
                TL_x, TL_y = lm_L[top_id][0] * 2.0 - 1.0 + jx, -(lm_L[top_id][1] * 2.0 - 1.0) + jy
                BL_x, BL_y = lm_L[bottom_id][0] * 2.0 - 1.0 + jx, -(lm_L[bottom_id][1] * 2.0 - 1.0) + jy

                # Right hand (TR and BR)
                TR_x, TR_y = lm_R[top_id][0] * 2.0 - 1.0 + jx, -(lm_R[top_id][1] * 2.0 - 1.0) + jy
                BR_x, BR_y = lm_R[bottom_id][0] * 2.0 - 1.0 + jx, -(lm_R[bottom_id][1] * 2.0 - 1.0) + jy

                # Assemble vertices (6 vertices total for 2 triangles)
                verts = np.array([
                    TL_x, TL_y, 0.0,   0.0, 0.0,
                    TR_x, TR_y, 0.0,   1.0, 0.0,
                    BR_x, BR_y, 0.0,   1.0, 1.0,
                    
                    TL_x, TL_y, 0.0,   0.0, 0.0,
                    BR_x, BR_y, 0.0,   1.0, 1.0,
                    BL_x, BL_y, 0.0,   0.0, 1.0,
                ], dtype=np.float32)

                # Borders of the quadrilateral (4 segments = 8 vertices)
                borders = np.array([
                    TL_x, TL_y, 0.0,  TR_x, TR_y, 0.0, # Top edge
                    TR_x, TR_y, 0.0,  BR_x, BR_y, 0.0, # Right edge
                    BR_x, BR_y, 0.0,  BL_x, BL_y, 0.0, # Bottom edge
                    BL_x, BL_y, 0.0,  TL_x, TL_y, 0.0, # Left edge
                ], dtype=np.float32)

                panels_to_render.append({
                    "vertices": verts,
                    "borders": borders,
                    "mode": mode,
                    "glitch_factor": glitch_factor
                })

                # Update cache
                last_panels_data[panel_idx] = {
                    "vertices": verts,
                    "borders": borders,
                    "mode": mode,
                    "glitch_factor": glitch_factor
                }
            
            lost_frames = 0
        else:
            # Tracking lost, use cached panels if within limit to prevent flickering
            if any(last_panels_data.values()) and lost_frames < lost_frames_limit:
                lost_frames += 1
                for panel_idx, cached in last_panels_data.items():
                    if cached is not None:
                        # Recalculate glitch factor for cached panels to decay smoothly
                        elapsed = current_time - last_cycle_time[panel_idx]
                        c_glitch = max(0.0, 1.0 - elapsed / 0.25)
                        
                        panels_to_render.append({
                            "vertices": cached["vertices"],
                            "borders": cached["borders"],
                            "mode": cached["mode"],
                            "glitch_factor": c_glitch
                        })
            else:
                last_panels_data = {0: None, 1: None, 2: None}
                lost_frames = 0

        # Render frame
        renderer.render(frame, panels_to_render, t_val)

        # Draw HUD (using title FPS display)
        fps = fps_counter.tick()
        hands_count = len(smoothed_hands)
        status = "Active" if len(panels_to_render) > 0 else "Waiting Hands"
        title = f"{renderer.title} - FPS: {fps:.0f} - {status} - Hands: {hands_count}"
        glfw.set_window_title(renderer.window, title)

        # Track active hands for the next frame
        active_hands_last_frame = {hand.label for hand in active_hands}

        glfw.swap_buffers(renderer.window)
        glfw.poll_events()

    logger.info("Closing application...")
    camera.stop()
    tracker.stop()
    raw_tracker.stop()
    renderer.cleanup()
    logger.info("Shutdown complete.")


if __name__ == "__main__":
    main()
