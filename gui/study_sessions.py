# gui/study_sessions.py
import customtkinter as ctk
from datetime import datetime
from database.db_manager import get_study_session_metrics


class StudySessionsView(ctk.CTkFrame):
    """Cozy view dashboard displaying interactive session calculation analytics."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.build_ui_layout()

    def build_ui_layout(self):
        """Builds components and maps data structures to real database stats."""
        # Wipe clean old layout memory structures to allow fluid page reloads
        for widget in self.winfo_children():
            widget.destroy()

        # Fetch live numbers from database backend script
        data = get_study_session_metrics()

        # ==========================================
        # TOP BANNER
        # ==========================================
        top_banner = ctk.CTkFrame(self, fg_color="transparent")
        top_banner.pack(fill="x", pady=(10, 15))

        lbl_title = ctk.CTkLabel(top_banner, text="Study Sessions 📖✨",
                                 font=ctk.CTkFont(family="Comic Sans MS", size=26, weight="bold"),
                                 text_color="#5e548e")
        lbl_title.pack(side="left", anchor="w")

        current_today = datetime.now().strftime("%d %B, %Y")
        lbl_date = ctk.CTkLabel(top_banner, text=f"📅 {current_today}",
                                font=ctk.CTkFont(family="Comic Sans MS", size=13, weight="bold"),
                                text_color="#4a4e69")
        lbl_date.pack(side="right", anchor="e", padx=10)

        # ==========================================
        # METRICS METRIC GRID OVERVIEW CARDS
        # ==========================================
        metrics_row = ctk.CTkFrame(self, fg_color="transparent")
        metrics_row.pack(fill="x", pady=(0, 15))

        # Card 1: Today's Target Progression Tracker
        t_hours = data["today_seconds"] / 3600.0
        pct_goal = min(100, int((t_hours / 5.0) * 100))  # 5-hour target benchmark baseline
        t_mins, _ = divmod(data["today_seconds"], 60)

        c1 = self.create_base_card(metrics_row, "#decfe6")
        ctk.CTkLabel(c1, text="Today's Progress", font=ctk.CTkFont(family="Comic Sans MS", size=12, weight="bold"),
                     text_color="#4a4e69").pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(c1, text=f"{pct_goal}% ⭐ {t_mins}m",
                     font=ctk.CTkFont(family="Comic Sans MS", size=16, weight="bold"), text_color="#5e548e").pack(
            pady=8)
        ctk.CTkLabel(c1, text="of 5h Goal", font=ctk.CTkFont(family="Comic Sans MS", size=10),
                     text_color="#bda0bc").pack()

        # Card 2: Consecutive Active Streak Days
        c2 = self.create_base_card(metrics_row, "#fcd5a1")
        ctk.CTkLabel(c2, text="Streak", font=ctk.CTkFont(family="Comic Sans MS", size=12, weight="bold"),
                     text_color="#4a4e69").pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(c2, text=f"{data['streak_days']} Days 🔥",
                     font=ctk.CTkFont(family="Comic Sans MS", size=16, weight="bold"), text_color="#ff7096").pack(
            pady=5)
        ctk.CTkLabel(c2, text="Keep it up!", font=ctk.CTkFont(family="Comic Sans MS", size=10, slant="italic"),
                     text_color="#e5989b").pack()

        # Card 3: All-Time Study Clock Accumulator
        tot_hours, remainder_secs = divmod(data["total_seconds"], 3600)
        tot_mins, _ = divmod(remainder_secs, 60)

        c3 = self.create_base_card(metrics_row, "#b7e4c7")
        ctk.CTkLabel(c3, text="Total Study Hours", font=ctk.CTkFont(family="Comic Sans MS", size=12, weight="bold"),
                     text_color="#4a4e69").pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(c3, text=f"🕒 {tot_hours}h {tot_mins}m",
                     font=ctk.CTkFont(family="Comic Sans MS", size=15, weight="bold"), text_color="#2a9d8f").pack(
            pady=8)
        ctk.CTkLabel(c3, text="All Time Logged", font=ctk.CTkFont(family="Comic Sans MS", size=10),
                     text_color="#4a4e69").pack()

        # Card 4: Focus Precision Mean
        c4 = self.create_base_card(metrics_row, "#decfe6")
        ctk.CTkLabel(c4, text="Average Focus", font=ctk.CTkFont(family="Comic Sans MS", size=12, weight="bold"),
                     text_color="#4a4e69").pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(c4, text=f"🎯 {data['avg_focus']}%",
                     font=ctk.CTkFont(family="Comic Sans MS", size=18, weight="bold"), text_color="#7209b7").pack(
            pady=5)
        ctk.CTkLabel(c4, text="Weekly Mean Index", font=ctk.CTkFont(family="Comic Sans MS", size=10),
                     text_color="#bda0bc").pack()

        # ==========================================
        # SPLIT MATRIX SECTION
        # ==========================================
        middle_row = ctk.CTkFrame(self, fg_color="transparent")
        middle_row.pack(fill="both", expand=True, pady=5)

        # LEFT SIDE: LEDGER CONTAINER FOR RECENT CARD ENTRIES
        self.recent_box = ctk.CTkFrame(middle_row, fg_color="#faf6ee", border_width=2, border_color="#decfe6",
                                       corner_radius=16)
        self.recent_box.pack(side="left", fill="both", expand=True, padx=(0, 10))

        lbl_recent_title = ctk.CTkLabel(self.recent_box, text="Recent Sessions Ledger",
                                        font=ctk.CTkFont(family="Comic Sans MS", size=14, weight="bold"),
                                        text_color="#5e548e")
        lbl_recent_title.pack(anchor="w", padx=15, pady=10)

        if not data["recent_sessions"]:
            ctk.CTkLabel(self.recent_box,
                         text="No tracking history logged yet.\nComplete a session to populate entries!",
                         font=ctk.CTkFont(family="Comic Sans MS", size=12, slant="italic"), text_color="#4a4e69").pack(
                pady=50)
        else:
            for item in data["recent_sessions"]:
                self.create_session_strip(item)

        # RIGHT SIDE: TROPHY ACHIEVEMENT RECOGNITION DECK
        right_box_stack = ctk.CTkFrame(middle_row, width=280, fg_color="transparent")
        right_box_stack.pack(side="right", fill="both", padx=(10, 0))
        right_box_stack.pack_propagate(False)

        ach_card = ctk.CTkFrame(right_box_stack, fg_color="#faf6ee", border_width=2, border_color="#c3b8a5",
                                corner_radius=16)
        ach_card.pack(fill="both", expand=True)
        ctk.CTkLabel(ach_card, text="🏆 Achievements unlocked",
                     font=ctk.CTkFont(family="Comic Sans MS", size=13, weight="bold"), text_color="#4a4e69").pack(
            anchor="w", padx=15, pady=10)

        # Award badges according to actual metrics
        achievements = []
        if tot_hours >= 10: achievements.append(("⭐ 10 Hours Achieve", "Dedicated Scholar"))
        if data["streak_days"] >= 7: achievements.append(("🔥 7 Days Streak", "Unstoppable Engine"))
        if data["avg_focus"] >= 90: achievements.append(("🎯 Focus Master", "Laser Precision Focus"))
        if not achievements: achievements.append(("🌱 Workspace Active", "Early Journey Stage"))

        for badge, detail in achievements:
            row_ach = ctk.CTkFrame(ach_card, fg_color="transparent")
            row_ach.pack(fill="x", padx=15, pady=6)
            ctk.CTkLabel(row_ach, text=badge, font=ctk.CTkFont(family="Comic Sans MS", size=12, weight="bold"),
                         text_color="#5e548e").pack(anchor="w")
            ctk.CTkLabel(row_ach, text=detail, font=ctk.CTkFont(family="Comic Sans MS", size=10, slant="italic"),
                         text_color="#bda0bc").pack(anchor="w", padx=22)

        # ==========================================
        # LOWER WORKSPACE FOOTER CONTEXT DECK
        # ==========================================
        bottom_row = ctk.CTkFrame(self, fg_color="transparent")
        bottom_row.pack(side="bottom", fill="x", pady=(15, 0))

        # Motivation Frame
        bot_left = ctk.CTkFrame(bottom_row, fg_color="#faf6ee", border_width=2, border_color="#decfe6",
                                corner_radius=16, height=110)
        bot_left.pack(side="left", expand=True, fill="both", padx=(0, 10))
        ctk.CTkLabel(bot_left, text="❝ Motivation", font=ctk.CTkFont(family="Comic Sans MS", size=12, weight="bold"),
                     text_color="#5e548e").pack(anchor="w", padx=15, pady=5)

        quote = "Discipline is choosing between what you want now and what you want most. 💜"
        ctk.CTkLabel(bot_left, text=quote, font=ctk.CTkFont(family="Comic Sans MS", size=12, slant="italic"),
                     text_color="#4a4e69", wraplength=380).pack(padx=15, pady=5)

        # Interactive Mood Feedback Panel
        self.bot_right = ctk.CTkFrame(bottom_row, fg_color="#faf6ee", border_width=2, border_color="#e5989b",
                                      corner_radius=16, height=110)
        self.bot_right.pack(side="right", expand=True, fill="both", padx=(10, 0))

        self.lbl_mood_title = ctk.CTkLabel(self.bot_right, text="How was today's study? 💕",
                                           font=ctk.CTkFont(family="Comic Sans MS", size=12, weight="bold"),
                                           text_color="#e5989b")
        self.lbl_mood_title.pack(anchor="w", padx=15, pady=5)

        mood_stack = ctk.CTkFrame(self.bot_right, fg_color="transparent")
        mood_stack.pack(fill="x", pady=5)

        for emoji in ["😊 Amazing", "😐 Good", "😴 Sleepy", "😫 Hard"]:
            ctk.CTkButton(
                mood_stack, text=emoji, width=60, height=30,
                font=ctk.CTkFont(family="Comic Sans MS", size=11),
                fg_color="#faf6ee", text_color="#4a4e69",
                border_width=1, border_color="#c3b8a5", hover_color="#f3ece0",
                command=lambda e=emoji: self.log_user_mood(e)
            ).pack(side="left", expand=True, padx=4)

    def create_base_card(self, parent, border_color):
        card = ctk.CTkFrame(parent, fg_color="#faf6ee", border_width=2, border_color=border_color, corner_radius=16,
                            height=85)
        card.pack(side="left", expand=True, fill="both", padx=6)
        card.pack_propagate(False)
        return card

    def create_session_strip(self, info):
        strip = ctk.CTkFrame(self.recent_box, fg_color="#faf6ee", height=45, border_width=1, border_color="#decfe6",
                             corner_radius=10)
        strip.pack(fill="x", pady=4, padx=15)
        strip.pack_propagate(False)

        ctk.CTkLabel(strip, text=f" 📖 {info['title']}",
                     font=ctk.CTkFont(family="Comic Sans MS", size=12, weight="bold"), text_color="#4a4e69").pack(
            side="left", padx=10)
        ctk.CTkLabel(strip, text=info["date"], font=ctk.CTkFont(family="Comic Sans MS", size=11),
                     text_color="#bda0bc").pack(side="left", padx=10)

        ctk.CTkLabel(strip, text=f"🎯 {info['focus']}", font=ctk.CTkFont(family="Comic Sans MS", size=11, weight="bold"),
                     text_color="#2a9d8f").pack(side="right", padx=15)
        ctk.CTkLabel(strip, text=f"⏱️ {info['time']}", font=ctk.CTkFont(family="Comic Sans MS", size=11),
                     text_color="#5e548e").pack(side="right", padx=10)

    def log_user_mood(self, chosen_mood):
        self.lbl_mood_title.configure(text=f"Logged as: {chosen_mood}! 🎉", text_color="#2a9d8f")