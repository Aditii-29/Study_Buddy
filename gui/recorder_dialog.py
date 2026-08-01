# gui/recorder_dialog.py
import customtkinter as ctk
import os
import time
import wave
import threading
import winsound
import numpy as np
import sounddevice as sd


class VoiceRecorderView(ctk.CTkFrame):
    def __init__(self, parent, on_save_callback, on_cancel_callback):
        super().__init__(parent, fg_color="#faf6ee", corner_radius=24, border_width=2, border_color="#decfe6")

        self.on_save_callback = on_save_callback
        self.on_cancel_callback = on_cancel_callback

        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 44100
        self.temp_file_path = None

        # Title Header
        self.lbl_status = ctk.CTkLabel(
            self, text="Record Your Motivational Alarm 🎙️",
            font=ctk.CTkFont(family="Comic Sans MS", size=20, weight="bold"),
            text_color="#5e548e"
        )
        self.lbl_status.pack(pady=(25, 5))

        # Live Recording Timer
        self.lbl_timer = ctk.CTkLabel(
            self, text="00:00",
            font=ctk.CTkFont(family="Courier", size=32, weight="bold"),
            text_color="#2a9d8f"
        )
        self.lbl_timer.pack(pady=10)

        # Name Entry Field
        self.entry_name = ctk.CTkEntry(
            self, placeholder_text="Track Title (e.g., Exam Day Motivation)",
            width=320, height=40, corner_radius=16,
            fg_color="#ffffff", text_color="#4a4e69", border_color="#decfe6"
        )
        self.entry_name.pack(pady=15)

        # Start / Stop Recording Button
        self.btn_record = ctk.CTkButton(
            self, text="🔴 Start Recording", width=180, height=42, corner_radius=21,
            font=ctk.CTkFont(family="Comic Sans MS", size=14, weight="bold"),
            fg_color="#ff7096", hover_color="#ff4d6d",
            command=self.toggle_recording
        )
        self.btn_record.pack(pady=10)

        # Control Row (Preview / Delete / Save)
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.pack(pady=15)

        self.btn_preview = ctk.CTkButton(
            self.actions_frame, text="▶ Preview", width=100, height=36, corner_radius=18,
            font=ctk.CTkFont(family="Comic Sans MS", size=12),
            fg_color="#faf6ee", text_color="#2a9d8f", border_width=2, border_color="#2a9d8f",
            hover_color="#eef8f6", state="disabled",
            command=self.preview_audio
        )
        self.btn_preview.pack(side="left", padx=6)

        self.btn_delete = ctk.CTkButton(
            self.actions_frame, text="🗑️ Delete", width=100, height=36, corner_radius=18,
            font=ctk.CTkFont(family="Comic Sans MS", size=12),
            fg_color="#faf6ee", text_color="#e63946", border_width=2, border_color="#e63946",
            hover_color="#fdeae8", state="disabled",
            command=self.delete_recording
        )
        self.btn_delete.pack(side="left", padx=6)

        self.btn_save = ctk.CTkButton(
            self.actions_frame, text="💾 Save", width=100, height=36, corner_radius=18,
            font=ctk.CTkFont(family="Comic Sans MS", size=12, weight="bold"),
            fg_color="#2a9d8f", hover_color="#218377", state="disabled",
            command=self.save_recording
        )
        self.btn_save.pack(side="left", padx=6)

        # Cancel / Back Button
        self.btn_cancel = ctk.CTkButton(
            self, text="← Back to Music List", width=160, height=32, corner_radius=16,
            font=ctk.CTkFont(family="Comic Sans MS", size=11),
            fg_color="transparent", text_color="#7209b7", hover_color="#f3ece0",
            command=self.cancel_view
        )
        self.btn_cancel.pack(pady=(5, 15))

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.audio_data = []

        self.btn_record.configure(text="⬛ Stop Recording", fg_color="#4a4e69")
        self.btn_preview.configure(state="disabled")
        self.btn_delete.configure(state="disabled")
        self.btn_save.configure(state="disabled")
        self.lbl_status.configure(text="Recording... Speak clearly! 🎙️", text_color="#ff7096")

        threading.Thread(target=self._record_audio_worker, daemon=True).start()
        self.start_time = time.time()
        self._update_timer()

    def _record_audio_worker(self):
        def callback(indata, frames, time_info, status):
            if self.is_recording:
                self.audio_data.append(indata.copy())

        with sd.InputStream(samplerate=self.sample_rate, channels=1, callback=callback):
            while self.is_recording:
                sd.sleep(100)

    def _update_timer(self):
        if self.is_recording:
            elapsed = int(time.time() - self.start_time)
            mins, secs = divmod(elapsed, 60)
            self.lbl_timer.configure(text=f"{mins:02d}:{secs:02d}")
            self.after(500, self._update_timer)

    def stop_recording(self):
        self.is_recording = False

        if not self.audio_data:
            self.lbl_status.configure(text="No audio recorded!", text_color="#e63946")
            self.btn_record.configure(text="🔴 Start Recording", fg_color="#ff7096")
            return

        recording_np = np.concatenate(self.audio_data, axis=0)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        temp_dir = os.path.join(base_dir, "assets", "temp")
        os.makedirs(temp_dir, exist_ok=True)
        self.temp_file_path = os.path.join(temp_dir, "temp_preview.wav")

        audio_int16 = (recording_np * 32767).astype(np.int16)
        with wave.open(self.temp_file_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_int16.tobytes())

        self.lbl_status.configure(text="Recording Finished! Preview or Save.", text_color="#2a9d8f")
        self.btn_record.configure(text="🔴 Re-record", fg_color="#ff7096")
        self.btn_preview.configure(state="normal")
        self.btn_delete.configure(state="normal")
        self.btn_save.configure(state="normal")

    def preview_audio(self):
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            winsound.PlaySound(self.temp_file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

    def delete_recording(self):
        self.audio_data = []
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            try:
                os.remove(self.temp_file_path)
            except Exception:
                pass
            self.temp_file_path = None

        self.lbl_timer.configure(text="00:00")
        self.lbl_status.configure(text="Deleted! Ready to record again.", text_color="#5e548e")
        self.btn_record.configure(text="🔴 Start Recording", fg_color="#ff7096")
        self.btn_preview.configure(state="disabled")
        self.btn_delete.configure(state="disabled")
        self.btn_save.configure(state="disabled")

    def save_recording(self):
        if not self.temp_file_path or not os.path.exists(self.temp_file_path):
            return

        title_text = self.entry_name.get().strip()
        if not title_text:
            title_text = f"My Motivation {int(time.time()) % 1000}"

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        target_dir = os.path.join(base_dir, "assets", "audio")
        os.makedirs(target_dir, exist_ok=True)

        import shutil
        final_filename = f"voice_{int(time.time())}.wav"
        final_path = os.path.join(target_dir, final_filename)

        shutil.move(self.temp_file_path, final_path)

        if self.on_save_callback:
            self.on_save_callback(title_text, final_path)

    def cancel_view(self):
        self.delete_recording()
        if self.on_cancel_callback:
            self.on_cancel_callback()