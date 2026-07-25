# gui/alarm_settings.py
import customtkinter as ctk
import os
import shutil
from tkinter import filedialog
import config
from Engine.audio_manager import play_synth_track_async


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
            border_width=2, border_color="#2a9d8f"
        )
        btn_record.pack(side="left", padx=10)

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

    # ==========================================
    # FILE SELECTION & DYNAMIC RENDER CONTROLLERS
    # ==========================================
    def handle_add_song_upload(self):
        """Opens file dialog picker to select custom sound file from computer."""
        file_path = filedialog.askopenfilename(
            title="Select Custom Alarm Track",
            filetypes=[("Audio Files", "*.mp3 *.wav")]
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
            self.toggle_heart_alarm(clean_title, custom_path=destination_path)

        except Exception as e:
            print(f"[FILE IMPORT ERROR] Could not import audio track: {str(e)}")

    def refresh_sound_vault_display(self):
        """Redraws the list items in the scrollable sound container."""
        for widget in self.sound_vault_box.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()

        all_tracks = self.default_tracks + self.custom_tracks
        for track in all_tracks:
            self.create_sound_track_row(track)

    def create_sound_track_row(self, track_info):
        """Renders an individual audio track card strip."""
        # 1. Create row strip container FIRST so 'row_strip' is defined
        row_strip = ctk.CTkFrame(
            self.sound_vault_box, fg_color="#faf6ee", height=50,
            border_width=2, border_color="#decfe6", corner_radius=16
        )
        row_strip.pack(fill="x", pady=5, padx=10)
        row_strip.pack_propagate(False)

        # 2. Define active status & heart icons FIRST so 'heart_icon' is defined
        current_active = self.ui_parent.selected_alarm_sound.get()
        is_active = (current_active == track_info["title"])

        heart_icon = "♥" if is_active else "♡"
        heart_text_color = "#ff4d6d" if is_active else "#ff7096"
        c_path = track_info.get("file_path", None)

        # 3. Add Play Button
        btn_play = ctk.CTkButton(
            row_strip, text="▶", width=30, height=30, corner_radius=15,
            font=ctk.CTkFont(size=11), fg_color="transparent",
            text_color=track_info["color"], border_width=2, border_color=track_info["color"],
            hover_color="#f3ece0",
            command=lambda: self.select_track_stream(track_info)
        )
        btn_play.pack(side="left", padx=15, pady=8)

        # 4. Add Song Title Label
        lbl_track_title = ctk.CTkLabel(
            row_strip, text=track_info["title"],
            font=ctk.CTkFont(family="Comic Sans MS", size=13, weight="bold"), text_color="#4a4e69"
        )
        lbl_track_title.pack(side="left", padx=5)

        # 5. Add Heart Button (Now heart_icon and row_strip exist!)
        btn_heart = ctk.CTkButton(
            row_strip, text=heart_icon, width=30, height=30,
            font=ctk.CTkFont(size=18), fg_color="transparent", text_color=heart_text_color,
            hover_color="#f3ece0",
            command=lambda t=track_info["title"], p=c_path: self.toggle_heart_alarm(t, custom_path=p)
        )
        btn_heart.pack(side="right", padx=15)

        # 6. Add Visual Audio Wave Representation
        lbl_wave = ctk.CTkLabel(
            row_strip, text=track_info["wave"],
            font=ctk.CTkFont(family="Courier", size=12), text_color="#bda0bc"
        )
        lbl_wave.pack(side="right", padx=20)

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