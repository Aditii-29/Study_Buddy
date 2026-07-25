# Engine/eye_tracker.py
import cv2
import numpy as np
import time
import os
import winsound
import config
import pygame
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


def run_eye_tracker(on_drowsy_callback=None, on_focused_callback=None, stop_check_callback=None, frame_callback=None):
    # Ensure 'face_landmarker.task' is downloaded and placed in the project root
    base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
        num_faces=1
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
    last_alarm_time = 0

    calibration_frames = 0
    open_ear_values = []
    calibrated_threshold = 0.20

    with vision.FaceLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            if stop_check_callback and stop_check_callback():
                break

            success, frame = cap.read()
            if not success:
                continue

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            results = landmarker.detect(mp_image)

            current_time = time.time()
            status = "Active!"
            color = (0, 255, 0)
            is_focused = True

            if results.face_landmarks:
                for face_landmarks in results.face_landmarks:
                    avg_ear = (calculate_ear(LEFT_EYE, face_landmarks) + calculate_ear(RIGHT_EYE, face_landmarks)) / 2.0
                    if calibration_frames < 30:
                        open_ear_values.append(avg_ear)
                        calibration_frames += 1
                        status = f"Calibrating Eyes... [{calibration_frames}/30]"
                        color = (0, 255, 255)

                        if calibration_frames == 30:
                            avg_open_ear = sum(open_ear_values) / 30.0
                            calibrated_threshold = avg_open_ear * 0.72
                            print(
                                f"[CALIBRATION SUCCESS] Avg Open EAR: {avg_open_ear:.3f} | Set Threshold to: {calibrated_threshold:.3f}")

                        is_focused = True
                    else:
                        if avg_ear < config.EAR_THRESHOLD:
                            if eye_closed_start_time is None:
                                eye_closed_start_time = current_time

                            time_elapsed = current_time - eye_closed_start_time

                            # ─── TIME LIMIT EXCEEDED: TRIGGER ALARM ───
                            if time_elapsed >= config.EYE_CLOSED_LIMIT_SECONDS:
                                status = "!!! WAKE UP !!!"
                                color = (0, 0, 255)
                                is_focused = False

                                # Check 2-second cooldown between sound plays
                                if current_time - last_alarm_time >= 2.0:
                                    last_alarm_time = current_time  # ◄── FIX 3: Update alarm timestamp!

                                    # ◄── FIX 1: Read correct config attribute CUSTOM_ALARM_FILE_PATH
                                    custom_path = getattr(config, "CUSTOM_ALARM_FILE_PATH", None)
                                    track_vibe = getattr(config, 'SELECTED_ALARM_TRACK', 'Morning Motivation')
                                    print(f"[ALARM TRIGGERED] Track: '{track_vibe}' | Custom Path: {custom_path}")

                                    # PATH A: Custom Uploaded Audio File
                                    if custom_path and os.path.exists(custom_path):
                                        import pygame
                                        try:
                                            if not pygame.mixer.get_init():
                                                pygame.mixer.init()
                                            pygame.mixer.music.load(custom_path)
                                            pygame.mixer.music.play()
                                            print(f"[AUDIO] Playing custom sound: {custom_path}")
                                        except Exception as e:
                                            print(f"[ALARM AUDIO ERROR] Failed playing custom sound: {e}")
                                            winsound.Beep(config.ALARM_FREQUENCY, config.ALARM_DURATION_MS)

                                    # PATH B: Default System Track Selection
                                    else:
                                        try:
                                            from Engine.audio_manager import play_synth_track_async
                                            play_synth_track_async(track_vibe)
                                            print(f"[AUDIO] Playing synth track: {track_vibe}")
                                        except Exception as e:
                                            print(f"[AUDIO ERROR] Synth playback failed: {e}")
                                            winsound.Beep(config.ALARM_FREQUENCY, config.ALARM_DURATION_MS)

                            # ─── WARNING STATE (Eyes closed, but threshold limit not reached yet) ───
                            else:  # ◄── FIX 2: Correctly aligned with `if time_elapsed >= config.EYE_CLOSED_LIMIT_SECONDS`
                                status = f"Drowsy... Warning in {int(config.EYE_CLOSED_LIMIT_SECONDS - time_elapsed) + 1}s"
                                color = (0, 165, 255)
                                is_focused = True
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

            cv2.putText(frame, f"STATUS: {status}", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            if frame_callback is not None:
                frame_callback(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()