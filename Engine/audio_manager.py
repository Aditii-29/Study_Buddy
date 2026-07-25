# Engine/audio_manager.py
import threading
import os
import winsound
import ctypes

winmm = ctypes.windll.winmm

SYSTEM_SOUNDS = {
    "Morning Motivation": "C:\\Windows\\Media\\chimes.wav",
    "Focus Time": "C:\\Windows\\Media\\notify.wav",
    "Deep Study": "C:\\Windows\\Media\\tada.wav",
    "Calm Piano": "C:\\Windows\\Media\\Speech On.wav",
    "Nature Vibes": "C:\\Windows\\Media\\Ring01.wav",
    "Lo-fi Beats": "C:\\Windows\\Media\\Alarm01.wav"
}


def play_synth_track_async(track_name_or_path):
    """Plays default WAV sounds or custom audio non-blockingly."""

    def run():
        try:
            sound_path = None

            # 1. Check if the argument is a custom file path on disk
            if track_name_or_path and os.path.exists(track_name_or_path):
                sound_path = track_name_or_path
            # 2. Check if it matches one of our default system track titles
            elif track_name_or_path in SYSTEM_SOUNDS:
                sound_path = SYSTEM_SOUNDS[track_name_or_path]

            # Fallback default if sound path is invalid/missing
            if not sound_path or not os.path.exists(sound_path):
                sound_path = "C:\\Windows\\Media\\chimes.wav"

            # ─── WAV FILE PLAYBACK ───
            if sound_path.lower().endswith(".wav"):
                # SND_FILENAME | SND_ASYNC plays sound in background without stopping the UI or blocking threads!
                winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

            # ─── MP3 OR OTHER AUDIO FORMATS (USING PYGAME) ───
            else:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()

            print(f"[AUDIO MANAGER] Playing audio track: {sound_path}")

        except Exception as e:
            print(f"[NATIVE AUDIO ERROR] Could not execute playback: {str(e)}")
            # Fallback beep if all sound drivers fail
            winsound.Beep(2500, 800)

    # Launch in thread so UI never freezes
    threading.Thread(target=run, daemon=True).start()