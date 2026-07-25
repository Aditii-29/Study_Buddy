# gui/live_monitoring.py
import customtkinter as ctk


class LiveMonitoringView(ctk.CTkFrame):
    """Isolated, cozy view architecture matching your reference sketch mockup."""

    def __init__(self, master, stop_session_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.stop_callback = stop_session_callback

        # ==========================================
        # TOP BANNER
        # ==========================================
        top_banner = ctk.CTkFrame(self, fg_color="transparent")
        top_banner.pack(fill="x", pady=(10, 15))

        lbl_live_title = ctk.CTkLabel(top_banner, text="Live Monitoring ✨",
                                      font=ctk.CTkFont(family="Comic Sans MS", size=26, weight="bold"),
                                      text_color="#5e548e")
        lbl_live_title.pack(anchor="w")
        lbl_live_sub = ctk.CTkLabel(top_banner, text="We're keeping an eye on you! ♡",
                                    font=ctk.CTkFont(family="Comic Sans MS", size=14, slant="italic"),
                                    text_color="#4a4e69")
        lbl_live_sub.pack(anchor="w", pady=(2, 0))

        # ==========================================
        # CENTER LAYOUT MATRIX SPLIT ROW
        # ==========================================
        center_split = ctk.CTkFrame(self, fg_color="transparent")
        center_split.pack(fill="both", expand=True)

        # LEFT SIDE: THE WEBCAM FOOTAGE BOX CARD
        video_card = ctk.CTkFrame(center_split, fg_color="#faf6ee", border_width=2, border_color="#bda0bc",
                                  corner_radius=16)
        video_card.pack(side="left", fill="both", expand=True, padx=(0, 15))

        video_header = ctk.CTkFrame(video_card, fg_color="transparent")
        video_header.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(video_header, text="🔴 Webcam Feed",
                     font=ctk.CTkFont(family="Comic Sans MS", size=13, weight="bold"), text_color="#5e548e").pack(
            side="left")
        ctk.CTkLabel(video_header, text="● REC 📶", font=ctk.CTkFont(family="Comic Sans MS", size=13),
                     text_color="#e5989b").pack(side="right")

        # The Actual Canvas Screen Render Label (Updated by Threading Loop)
        self.live_video_label = ctk.CTkLabel(video_card,
                                             text="🎥 Session is Not Started\nGo to the Home Hub to begin tracking!",
                                             font=ctk.CTkFont(size=14), fg_color="#f5f2eb", corner_radius=10)
        self.live_video_label.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # RIGHT SIDE: STATUS TELEMETRY CARDS
        right_stack = ctk.CTkFrame(center_split, width=220, fg_color="transparent")
        right_stack.pack(side="right", fill="y")
        right_stack.pack_propagate(False)

        # 1. Eye Status Card
        card_eye = ctk.CTkFrame(right_stack, fg_color="#faf6ee", border_width=1, border_color="#c3b8a5",
                                corner_radius=12, height=75)
        card_eye.pack(fill="x", pady=4)
        card_eye.pack_propagate(False)
        ctk.CTkLabel(card_eye, text="👁️ Eye Status", font=ctk.CTkFont(family="Comic Sans MS", size=12, weight="bold"),
                     text_color="#4a4e69").pack(anchor="w", padx=10, pady=(5, 0))
        self.lbl_live_eye_val = ctk.CTkLabel(card_eye, text="Idle",
                                             font=ctk.CTkFont(family="Comic Sans MS", size=16, weight="bold"),
                                             text_color="#4a4e69")
        self.lbl_live_eye_val.pack(anchor="w", padx=15)

        # 2. Focus Level Card
        card_focus = ctk.CTkFrame(right_stack, fg_color="#faf6ee", border_width=1, border_color="#c3b8a5",
                                  corner_radius=12, height=90)
        card_focus.pack(fill="x", pady=4)
        card_focus.pack_propagate(False)
        ctk.CTkLabel(card_focus, text="🎯 Focus Level", font=ctk.CTkFont(family="Comic Sans MS", size=12, weight="bold"),
                     text_color="#4a4e69").pack(anchor="w", padx=10, pady=(5, 0))
        self.lbl_live_focus_val = ctk.CTkLabel(card_focus, text="--%",
                                               font=ctk.CTkFont(family="Comic Sans MS", size=26, weight="bold"),
                                               text_color="#4a4e69")
        self.lbl_live_focus_val.pack(pady=2)

        # 3. Head Posture Card
        card_posture = ctk.CTkFrame(right_stack, fg_color="#faf6ee", border_width=1, border_color="#c3b8a5",
                                    corner_radius=12, height=75)
        card_posture.pack(fill="x", pady=4)
        card_posture.pack_propagate(False)
        ctk.CTkLabel(card_posture, text="👤 Head Posture",
                     font=ctk.CTkFont(family="Comic Sans MS", size=12, weight="bold"), text_color="#4a4e69").pack(
            anchor="w", padx=10, pady=(5, 0))
        self.lbl_live_posture_val = ctk.CTkLabel(card_posture, text="Idle",
                                                 font=ctk.CTkFont(family="Comic Sans MS", size=14, weight="bold"),
                                                 text_color="#4a4e69")
        self.lbl_live_posture_val.pack(anchor="w", padx=15)

        # ==========================================
        # BOTTOM ROW: SESSION TIMERS TRIO
        # ==========================================
        timers_row = ctk.CTkFrame(self, fg_color="transparent")
        timers_row.pack(side="bottom", fill="x", pady=(15, 0))

        # Card A: Session Timer
        t_card1 = ctk.CTkFrame(timers_row, fg_color="#faf6ee", border_width=1, border_color="#e5989b", corner_radius=12,
                               height=85)
        t_card1.pack(side="left", expand=True, fill="both", padx=4)
        ctk.CTkLabel(t_card1, text="⏳ Session Timer", font=ctk.CTkFont(family="Comic Sans MS", size=11, weight="bold"),
                     text_color="#4a4e69").pack(pady=(8, 0))
        self.lbl_live_session_clock = ctk.CTkLabel(t_card1, text="00:50:00",
                                                   font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
                                                   text_color="#5e548e")
        self.lbl_live_session_clock.pack()

        # Card B: Sleep Timer
        t_card2 = ctk.CTkFrame(timers_row, fg_color="#faf6ee", border_width=1, border_color="#bda0bc", corner_radius=12,
                               height=85)
        t_card2.pack(side="left", expand=True, fill="both", padx=4)
        ctk.CTkLabel(t_card2, text="💤 Sleep Timer", font=ctk.CTkFont(family="Comic Sans MS", size=11, weight="bold"),
                     text_color="#4a4e69").pack(pady=(8, 0))
        ctk.CTkLabel(t_card2, text="00:00", font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
                     text_color="#e5989b").pack()

        # Card C: Cute Break Reminder Status Card (Replaces the Button layout)
        t_card3 = ctk.CTkFrame(timers_row, fg_color="#faf6ee", border_width=1, border_color="#c3b8a5", corner_radius=12,
                               height=85)
        t_card3.pack(side="left", expand=True, fill="both", padx=4)
        ctk.CTkLabel(t_card3, text="☕ Break Reminder", font=ctk.CTkFont(family="Comic Sans MS", size=11, weight="bold"),
                     text_color="#4a4e69").pack(pady=(8, 0))

        self.lbl_break_status = ctk.CTkLabel(t_card3, text="Focusing...",
                                             font=ctk.CTkFont(family="Comic Sans MS", size=16, weight="bold"),
                                             text_color="#2a9d8f")
        self.lbl_break_status.pack(pady=4)

    # ==========================================
    # DYNAMIC STATE ENGINE CONTROLLERS
    # ==========================================
    def update_ui_state(self, session_running):
        """Updates internal views and clears lingering frame captures without utilizing a button."""
        if session_running:
            self.lbl_break_status.configure(text="Session Active ⚡", text_color="#5e548e")
        else:
            self.lbl_break_status.configure(text="Focus Idle 💤", text_color="#4a4e69")

            # Clear old webcam frame snapshots completely away from memory view limits
            self.live_video_label.configure(
                image="",
                text="🎥 Session is Not Started\nGo to the Home Hub to begin tracking!"
            )
            self.live_video_label.image = None

            # Clean up the dashboard's side telemetry stats back to default states
            self.lbl_live_eye_val.configure(text="Idle", text_color="#4a4e69")
            self.lbl_live_focus_val.configure(text="--%", text_color="#4a4e69")
            self.lbl_live_posture_val.configure(text="Idle", text_color="#4a4e69")