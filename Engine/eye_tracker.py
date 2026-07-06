# Engine/eye_tracker.py
import cv2
import numpy as np
import time
import winsound
import config
from mediapipe.python.solutions import face_mesh as mp_face_mesh


def run_eye_tracker(on_drowsy_callback=None, on_focused_callback=None, stop_check_callback=None, frame_callback=None):
    """
    Runs the tracking engine with a controlled alarm cooldown to prevent stuttering.
    """
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1, refine_landmarks=True,
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    )

    LEFT_EYE = [362, 385, 387, 263, 373, 380]
    RIGHT_EYE = [33, 160, 158, 133, 153, 144]

    def calculate_ear(eye_landmarks, landmarks):
        p1 = np.array([landmarks[eye_landmarks[0]].x, landmarks[eye_landmarks[0]].y])
        p4 = np.array([landmarks[eye_landmarks[3]].x, landmarks[eye_landmarks[3]].y])
        p2 = np.array([landmarks[eye_landmarks[1]].x, landmarks[eye_landmarks[1]].y])
        p6 = np.array([landmarks[eye_landmarks[5]].x, landmarks[eye_landmarks[5]].y])
        p3 = np.array([landmarks[eye_landmarks[2]].x, landmarks[eye_landmarks[2]].y])
        p5 = np.array([landmarks[eye_landmarks[4]].x, landmarks[eye_landmarks[4]].y])
        return (np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)) / (2.0 * np.linalg.norm(p1 - p4))

    cap = cv2.VideoCapture(0)
    eye_closed_start_time = None
    last_alarm_time = 0  # Tracks when the alarm last sounded

    while cap.isOpened():
        if stop_check_callback and stop_check_callback():
            break

        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        current_time = time.time()
        status = "Active!"
        color = (0, 255, 0)
        is_focused = True

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                avg_ear = (calculate_ear(LEFT_EYE, landmarks) + calculate_ear(RIGHT_EYE, landmarks)) / 2.0

                if avg_ear < config.EAR_THRESHOLD:
                    if eye_closed_start_time is None:
                        eye_closed_start_time = current_time

                    time_elapsed = current_time - eye_closed_start_time
                    if time_elapsed >= config.EYE_CLOSED_LIMIT_SECONDS:
                        status = "!!! WAKE UP !!!"
                        color = (0, 0, 255)
                        is_focused = False

                        # ALARM COOLDOWN: Only beep if 2 seconds have passed since the last beep
                        if current_time - last_alarm_time >= 2.0:
                            winsound.Beep(config.ALARM_FREQUENCY, config.ALARM_DURATION_MS)
                            last_alarm_time = current_time
                    else:
                        status = f"Drowsy... Warning in {int(config.EYE_CLOSED_LIMIT_SECONDS - time_elapsed) + 1}s"
                        color = (0, 165, 255)
                else:
                    eye_closed_start_time = None
        else:
            status = "No Face Detected"
            color = (0, 0, 255)
            is_focused = False

        if is_focused and on_focused_callback:
            on_focused_callback()
        elif not is_focused and on_drowsy_callback:
            on_drowsy_callback()

            # Add the tracking status overlay onto the video frames matrix
        cv2.putText(frame, f"STATUS: {status}", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            # 1. NEW LOGIC: Pass the frame directly to your GUI dashboard thread instead of opening a window
        if frame_callback is not None:
                frame_callback(frame)

            # 2. REMOVED cv2.imshow: This stops the extra pop-up window from opening!
            # cv2.imshow('Study Guardian AI - Phase 1 Engine', frame)

            # We keep a tiny delay frame sleep tick to maintain the loop lifecycle sync
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()