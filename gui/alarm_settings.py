# gui/alarm_settings.py
import customtkinter as ctk
import os
import shutil
import json
from pathlib import Path
from tkinter import filedialog
from Engine.audio_manager import play_synth_track_async
from gui.recorder_dialog import VoiceRecorderView

class AlarmSettingsView(ctk.CTkFrame):
    def __init__(self, master, ui_parent):
        super().__init__(master, fg_color="transparent")
        self.ui_parent = ui_parent

        # List of default sound tracks
        self.default_tracks = [
            {"title": "Morning Motivation", "color": "#9b5de5", "wave": " 〰️𝔽𝕠𝕔𝕦𝕤〰️ "},
            {"title": "Focus Time", "color": "#2a9d8f", "wave": " 〰️𝔸𝕝𝕚𝕧𝕖〰️ "},
            {"title": "Deep Study", "color": "#00b4d8", "wave": " 〰️𝔻𝕖𝕖𝕡〰️ "},
            {"title": "Calm Piano", "color": "#ff7096", "wave": " 〰️𝕊𝕠𝕗𝕥〰️ "},
            {"title": "Nature Vibes", "color": "#ffb703", "wave": " 〰️𝕎𝕚𝕝𝕕〰️ "},
            {"title": "Lo-fi Beats", "color": "#7209b7", "wave": " 〰️ℂ𝕙𝕚𝕝𝕝〰️ "}
        ]

        # Array to track user-added custom uploaded audio tracks
        self.custom_tracks = []
        self.load_custom_tracks_from_disk()

        # ==========================================
        # TOP CONTAINER: HEADER TITLE LAYOUT
        # ==========================================
        lbl_title = ctk.CTkLabel(
            self, text="⚡ Alarm ⚡",
            font=ctk.CTkFont(family="Comic Sans MS", size=36, weight="bold"), text_color="#5e548e"
        )
        lbl_title.pack(pady=(20, 5))

        lbl_subtitle = ctk.CTkLabel(
            self, text="Choose your fav\n✨ Music ✨",
            font=ctk.CTkFont(family="Comic Sans MS", size=20, weight="bold"), text_color="#4a4e69",
            justify="center"
        )
        lbl_subtitle.pack(pady=(0, 20))

        # ==========================================
        # MID CONTAINER: UTILITY BUTTON TRACKS
        # ==========================================
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(pady=(0, 20))

        btn_add_song = ctk.CTkButton(
            buttons_frame, text="+ Add Song", width=130, height=38, corner_radius=20,
            font=ctk.CTkFont(family="Comic Sans MS", size=13),
            fg_color="#faf6ee", text_color="#ff7096", hover_color="#fcecee",
            border_width=2, border_color="#ff7096",
            command=self.handle_add_song_upload
        )
        btn_add_song.pack(side="left", padx=10)

        btn_record = ctk.CTkButton(
            buttons_frame, text="Record  🎙️", width=130, height=38, corner_radius=20,
            font=ctk.CTkFont(family="Comic Sans MS", size=13),
            fg_color="#faf6ee", text_color="#2a9d8f", hover_color="#eef8f6",
            border_width=2, border_color="#2a9d8f",
            command=self.show_recording_page
        )
        btn_record.pack(side="left", padx=10)

        # Create recorder view frame (hidden by default)
        self.recorder_view = VoiceRecorderView(
            self,
            on_save_callback=self.handle_recorded_voice_save,
            on_cancel_callback=self.show_sound_list_page
        )

        # ==========================================
        # MAIN DOCK CONTAINER: THE SCROLLABLE SOUND BOX
        # ==========================================
        self.sound_vault_box = ctk.CTkScrollableFrame(
            self, width=540, height=360, fg_color="#f0ebf7",
            border_width=2, border_color="#decfe6", corner_radius=24
        )
        self.sound_vault_box.pack(pady=10, fill="x", padx=40)

        lbl_vault_header = ctk.CTkLabel(
            self.sound_vault_box, text="🎵 Default & Custom Sounds",
            font=ctk.CTkFont(family="Comic Sans MS", size=15, weight="bold"), text_color="#5e548e"
        )
        lbl_vault_header.pack(anchor="w", padx=15, pady=(10, 15))

        # Refresh display after sound_vault_box is created
        self.refresh_sound_vault_display()

        # ==========================================
        # LOWER FOOTER CONTEXT DECORATION
        # ==========================================
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", pady=(15, 10), padx=40)

        lbl_footer_hint = ctk.CTkLabel(
            footer_frame, text="⭐ Pick a vibe that keeps you going! 💕",
            font=ctk.CTkFont(family="Comic Sans MS", size=13, slant="italic"), text_color="#e5989b"
        )
        lbl_footer_hint.pack(side="left", padx=10)

        lbl_speaker_doodle = ctk.CTkLabel(
            footer_frame, text="🔊📻", font=ctk.CTkFont(size=24)
        )
        lbl_speaker_doodle.pack(side="right", padx=10)

    def show_recording_page(self):
        """Swaps the view to show the recorder interface."""
        self.sound_vault_box.pack_forget()
        self.recorder_view.pack(fill="both", expand=True, pady=10)

    def show_sound_list_page(self):
        """Swaps back to the sound list."""
        self.recorder_view.pack_forget()
        self.sound_vault_box.pack(fill="both", expand=True)

    def handle_recorded_voice_save(self, title_text, file_path):
        """Saves voice note, adds to list, and restores sound list view."""
        clean_title = f"🎙️ {title_text}"
        new_track = {
            "title": clean_title,
            "file_path": file_path,
            "color": "#2a9d8f",
            "wave": " 〰️𝕍𝕠𝕚𝕔𝕖〰️ "
        }
        self.custom_tracks.append(new_track)
        self.save_custom_tracks_to_disk()
        self.toggle_heart_alarm(clean_title, custom_path=file_path)
        self.show_sound_list_page()

    def delete_custom_track(self, track_info):
        """Deletes custom sound file from disk and removes it from the UI list."""
        file_path = track_info.get("file_path", None)
        track_title = track_info.get("title", "")

        # 1. Remove file from disk if it exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"[TRACK DELETED] Removed file from disk: {file_path}")
            except Exception as e:
                print(f"[DELETE ERROR] Could not remove file: {e}")

        # 2. Remove track from internal custom list
        self.custom_tracks = [t for t in self.custom_tracks if t["title"] != track_title]
        self.save_custom_tracks_to_disk()

        # 3. If deleted track was the active alarm, reset to default track
        if self.ui_parent.selected_alarm_sound.get() == track_title:
            self.toggle_heart_alarm("Morning Motivation", custom_path=None)

        # 4. Refresh display
        self.refresh_sound_vault_display()

    # ==========================================
    # FILE SELECTION & DYNAMIC RENDER CONTROLLERS
    # ==========================================
    def handle_add_song_upload(self):
        """Opens file dialog picker specifically configured for Audio Files."""
        user_music_dir = os.path.expanduser("~/Music")
        initial_dir = user_music_dir if os.path.exists(user_music_dir) else "/"

        file_path = filedialog.askopenfilename(
            title="Select Custom Audio Track 🎵",
            initialdir=initial_dir,
            filetypes=[
                ("Audio Files (*.mp3, *.wav, *.m4a, *.ogg)", "*.mp3 *.wav *.m4a *.ogg"),
                ("MP3 Audio (*.mp3)", "*.mp3"),
                ("WAV Audio (*.wav)", "*.wav"),
                ("M4A Audio (*.m4a)", "*.m4a"),
                ("All Files (*.*)", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            target_dir = os.path.join(base_dir, "assets", "audio")
            os.makedirs(target_dir, exist_ok=True)

            filename = os.path.basename(file_path)
            destination_path = os.path.join(target_dir, filename)
            shutil.copy(file_path, destination_path)

            clean_title = os.path.splitext(filename)[0].replace("_", " ").title()

            new_track = {
                "title": clean_title,
                "file_path": destination_path,
                "color": "#ff7096",
                "wave": " 〰️ℂ𝕦𝕤𝕥𝕠𝕞〰️ "
            }

            self.custom_tracks.append(new_track)
            self.save_custom_tracks_to_disk()
            self.toggle_heart_alarm(clean_title, custom_path=destination_path)

        except Exception as e:
            print(f"[FILE IMPORT ERROR] Could not import track: {str(e)}")

    def refresh_sound_vault_display(self):
        """Redraws the list items in the scrollable sound container."""
        for widget in self.sound_vault_box.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()

        all_tracks = self.default_tracks + self.custom_tracks
        for track in all_tracks:
            self.create_sound_track_row(track)

    def _get_storage_file(self):
        """Returns the path to the custom tracks JSON storage file."""
        storage_dir = Path(__file__).resolve().parent.parent / "assets"
        storage_dir.mkdir(parents=True, exist_ok=True)
        return storage_dir / "custom_tracks.json"

    def save_custom_tracks_to_disk(self):
        """Saves current custom tracks list to JSON file."""
        try:
            storage_file = self._get_storage_file()
            with open(storage_file, "w", encoding="utf-8") as f:
                json.dump(self.custom_tracks, f, indent=4)
            print("[STORAGE] Saved custom tracks to disk.")
        except Exception as e:
            print(f"[STORAGE ERROR] Could not save tracks: {e}")

    def load_custom_tracks_from_disk(self):
        """Loads saved custom tracks from JSON file when app starts."""
        storage_file = self._get_storage_file()
        if storage_file.exists():
            try:
                with open(storage_file, "r", encoding="utf-8") as f:
                    saved_tracks = json.load(f)
                    # Keep only tracks whose audio files still exist on disk
                    self.custom_tracks = [
                        t for t in saved_tracks if Path(t["file_path"]).exists()
                    ]
                print(f"[STORAGE] Loaded {len(self.custom_tracks)} custom tracks.")
            except Exception as e:
                print(f"[STORAGE ERROR] Could not load tracks: {e}")
                self.custom_tracks = []
        else:
            self.custom_tracks = []

    def create_sound_track_row(self, track_info):
        """Renders an individual sound card item."""
        row_strip = ctk.CTkFrame(
            self.sound_vault_box, fg_color="#faf6ee", height=50,
            border_width=2, border_color="#decfe6", corner_radius=16
        )
        row_strip.pack(fill="x", pady=5, padx=10)
        row_strip.pack_propagate(False)

        current_active = self.ui_parent.selected_alarm_sound.get()
        is_active = (current_active == track_info["title"])

        heart_icon = "♥" if is_active else "♡"
        heart_text_color = "#ff4d6d" if is_active else "#ff7096"
        c_path = track_info.get("file_path", None)

        # Play / Preview Button
        btn_play = ctk.CTkButton(
            row_strip, text="▶", width=30, height=30, corner_radius=15,
            font=ctk.CTkFont(size=11), fg_color="transparent",
            text_color=track_info["color"], border_width=2, border_color=track_info["color"],
            hover_color="#f3ece0",
            command=lambda: self.select_track_stream(track_info)
        )
        btn_play.pack(side="left", padx=15, pady=8)

        # Track Title
        lbl_track_title = ctk.CTkLabel(
            row_strip, text=track_info["title"],
            font=ctk.CTkFont(family="Comic Sans MS", size=13, weight="bold"), text_color="#4a4e69"
        )
        lbl_track_title.pack(side="left", padx=5)

        # Heart / Favorite Button
        btn_heart = ctk.CTkButton(
            row_strip, text=heart_icon, width=30, height=30,
            font=ctk.CTkFont(size=18), fg_color="transparent", text_color=heart_text_color,
            hover_color="#f3ece0",
            command=lambda t=track_info["title"], p=c_path: self.toggle_heart_alarm(t, custom_path=p)
        )
        btn_heart.pack(side="right", padx=10)

        # Delete Button (Only shown for custom/uploaded/recorded tracks!)
        if c_path:
            btn_delete_track = ctk.CTkButton(
                row_strip, text="🗑️", width=28, height=28, corner_radius=14,
                font=ctk.CTkFont(size=12), fg_color="transparent", text_color="#e63946",
                hover_color="#fdeae8",
                command=lambda t=track_info: self.delete_custom_track(t)
            )
            btn_delete_track.pack(side="right", padx=5)

        # Wave Label
        lbl_wave = ctk.CTkLabel(
            row_strip, text=track_info["wave"],
            font=ctk.CTkFont(family="Courier", size=12), text_color="#bda0bc"
        )
        lbl_wave.pack(side="right", padx=10)

    def toggle_heart_alarm(self, track_title, custom_path=None):
        """Sets the selected track as active and clears out old paths if default sound picked."""
        self.ui_parent.selected_alarm_sound.set(track_title)

        import config
        config.SELECTED_ALARM_TRACK = track_title
        config.CUSTOM_ALARM_FILE_PATH = custom_path

        print(f"[ALARM HEART UPDATED] Track: '{track_title}' | Custom File Path: {custom_path}")

        self.refresh_sound_vault_display()

    def select_track_stream(self, track_info):
        """Previews track playback when play arrow is clicked."""
        title = track_info["title"]
        self.ui_parent.selected_alarm_sound.set(title)

        c_path = track_info.get("file_path", None)

        import config
        config.SELECTED_ALARM_TRACK = title
        config.CUSTOM_ALARM_FILE_PATH = c_path

        if c_path and os.path.exists(c_path):
            import pygame
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(c_path)
                pygame.mixer.music.play()
            except Exception as err:
                print(f"[PREVIEW ERROR] Could not play custom file: {err}")
        else:
            play_synth_track_async(title)