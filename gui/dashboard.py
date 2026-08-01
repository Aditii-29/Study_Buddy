# gui/dashboard.py
import customtkinter as ctk
import os
import sys
import threading
import queue
import time
import sqlite3

import mediapipe as mp
from numpy.ma.core import size
from gui.reports import ReportsView
from gui.alarm_settings import AlarmSettingsView

# Ensure root directory is in system path so we can import cleanly from other layers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from Engine.eye_tracker import run_eye_tracker
from database.db_manager import log_study_session, DB_PATH
from gui.live_monitoring import LiveMonitoringView
from Engine.auth_backend import login_user, register_user
from gui.study_sessions import StudySessionsView

class StudyGuardianUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ==========================================
        # WINDOW TOPOGRAPHY (Uizard Warm Beige Theme)
        # ==========================================
        self.title("Study Buddy")
        self.geometry("1020x660")
        self.resizable(True, True)

        # Setting a soft pastel, study-friendly background surface
        ctk.set_appearance_mode("light")
        self.configure(fg_color="#faf6ee")  # Warm soft beige backdrop tint

        # App Core State Tracking Variables
        self.session_running = False
        self.active_tab = "focus"
        self.current_visible_content_frame = None
        self.sidebar_expanded = False  # Start expanded to display our beautiful handcrafted layout names
        self.study_seconds_left = config.STUDY_MINUTES * 60
        self.total_session_seconds = config.STUDY_MINUTES * 60
        self.drowsy_alerts_count = 0
        self.was_drowsy_last_frame = False
        self.last_clock_tick = time.time()

        self.status_queue = queue.Queue()
        self.protocol("WM_DELETE_WINDOW",self.on_closing)

        self.selected_alarm_sound = ctk.StringVar(value="Classic Beep")
        self.alarm_volume = ctk.DoubleVar(value=0.7)
        self.drowsy_time_threshold = ctk.IntVar(value=2)
        # Initialize Container Frames for States
        self.login_view_frame = None
        self.main_view_frame = None
        self.alarm_canvas=None

        # Build structures and launch the Login screen immediately
        self.create_login_screen_layout()
        self.show_login_screen()

        # Start persistent UI engine loop manager
        self.update_timer_loop()

    # ========================================================
    # STATE VIEW 1: THE WELCOME / LOGIN SCREEN
    # ========================================================
    def create_login_screen_layout(self):
        """Builds a beautiful cozy matching login and registration layout entry gate."""
        self.login_view_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.is_register_mode = False  # Track state toggle cleanly

        # Welcoming Header Labels
        self.lbl_welcome_title = ctk.CTkLabel(
            self.login_view_frame, text="Welcome, Study Buddy",
            font=ctk.CTkFont(family="Comic Sans MS", size=38, weight="bold"), text_color="#5e548e"
        )
        self.lbl_welcome_title.pack(pady=(80, 10))

        self.lbl_welcome_sub = ctk.CTkLabel(
            self.login_view_frame, text="Enter your workspace credentials to join your desk.",
            font=ctk.CTkFont(family="Comic Sans MS", size=15), text_color="#4a4e69"
        )
        self.lbl_welcome_sub.pack(pady=(0, 30))

        # Input Forms Matrix Wrapper
        form_frame = ctk.CTkFrame(self.login_view_frame, fg_color="transparent")
        form_frame.pack(pady=10)

        self.entry_username = ctk.CTkEntry(
            form_frame, placeholder_text="Username", width=300, height=45, corner_radius=12,
            border_width=2, border_color="#5e548e", fg_color="#faf6ee", text_color="#4a4e69",
            font=ctk.CTkFont(family="Comic Sans MS", size=13)
        )
        self.entry_username.pack(pady=10)

        # Added dynamic Email Input tracking field structure cleanly
        self.entry_email = ctk.CTkEntry(
            form_frame, placeholder_text="Email Address", width=300, height=45, corner_radius=12,
            border_width=2, border_color="#5e548e", fg_color="#faf6ee", text_color="#4a4e69",
            font=ctk.CTkFont(family="Comic Sans MS", size=13)
        )
        # Hidden by default because we start in Login Mode!
        self.entry_email.pack_forget()

        self.entry_password = ctk.CTkEntry(
            form_frame, placeholder_text="Password", show="*", width=300, height=45, corner_radius=12,
            border_width=2, border_color="#5e548e", fg_color="#faf6ee", text_color="#4a4e69",
            font=ctk.CTkFont(family="Comic Sans MS", size=13)
        )
        self.entry_password.pack(pady=10)

        # Main Action Execution Button
        self.btn_login_trigger = ctk.CTkButton(
            self.login_view_frame, text="Enter Workspace  →",
            width=300, height=50, corner_radius=16,
            font=ctk.CTkFont(family="Comic Sans MS", size=16, weight="bold"),
            fg_color="#5e548e", text_color="#ffffff", hover_color="#4d4475",
            border_width=2, border_color="#5e548e",
            command=self.authenticate_and_launch_dashboard
        )
        self.btn_login_trigger.pack(pady=20)

        # Soft underground switch label tracking option link
        self.btn_toggle_mode = ctk.CTkButton(
            self.login_view_frame, text="Don't have an account? Register here",
            font=ctk.CTkFont(family="Comic Sans MS", size=12, underline=True),
            fg_color="transparent", text_color="#5e548e", hover_color="#faf6ee",
            command=self.toggle_auth_view_mode
        )
        self.btn_toggle_mode.pack(pady=5)

    def toggle_auth_view_mode(self):
        """Swaps view layouts between clean Login forms and complete Registration paths dynamically."""
        if not self.is_register_mode:
            self.is_register_mode = True
            self.lbl_welcome_title.configure(text="Create Account")
            self.lbl_welcome_sub.configure(text="Sign up below to secure your workspace profile.")
            self.entry_email.pack(after=self.entry_username, pady=10)  # Reveal email field
            self.btn_login_trigger.configure(text="Complete Registration  ✓")
            self.btn_toggle_mode.configure(text="Already have an account? Sign In instead")
        else:
            self.is_register_mode = False
            self.lbl_welcome_title.configure(text="Welcome, Study Buddy")
            self.lbl_welcome_sub.configure(text="Enter your workspace credentials to join your desk.")
            self.entry_email.pack_forget()  # Hide email field layout cleanly
            self.btn_login_trigger.configure(text="Enter Workspace  →")
            self.btn_toggle_mode.configure(text="Don't have an account? Register here")

    def show_login_screen(self):
        """Mounts the login window to full view."""
        if self.main_view_frame:
            self.main_view_frame.pack_forget()
        self.login_view_frame.pack(fill="both", expand=True)

    def authenticate_and_launch_dashboard(self):
        """Verifies access input parameters via MongoDB backend routing and cleanly transitions into workspace."""
        from tkinter import messagebox

        # Pull text directly from custom elements
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        # ==========================================
        # PATH PATH A: USER REGISTRATION EXECUTION
        # ==========================================
        if hasattr(self, 'is_register_mode') and self.is_register_mode:
            email = self.entry_email.get().strip()

            # Execute database insertion request pipeline
            success, message = register_user(username, email, password)

            if success:
                messagebox.showinfo("Registration Success", message)
                # Toggle interface look back to Login cleanly
                self.toggle_auth_view_mode()
                # Clear security fields for safety
                self.entry_password.delete(0, 'end')
            else:
                messagebox.showerror("Registration Error", message)
            return

        # ==========================================
        # PATH PATH B: USER LOGIN VERIFICATION EXECUTION
        # ==========================================
        else:
            # We treat the username box as the login field (adjust to email if preferred)
            # For uniformity matching auth_backend.py, we assume they input their email into the box
            success, result_or_username = login_user(username, password)

            if success:
                print(f"[AUTH SYSTEM] Access Granted for profile target: {result_or_username}")
                messagebox.showinfo("Access Granted", f"Welcome back to your desk, {result_or_username}!")

                # Unpack Login, build, and deploy the main dual-column dashboard
                self.login_view_frame.pack_forget()
                self.create_main_dashboard_layout()
                self.main_view_frame.pack(fill="both", expand=True)
            else:
                messagebox.showerror("Authentication Failed", result_or_username)
    # STATE VIEW 2: THE MAIN WORKSPACE INTERFACE LAYOUT
    # ========================================================
    def create_main_dashboard_layout(self):
        """Constructs a split-screen layout with a dynamic expandable/collapsible sidebar."""
        self.main_view_frame = ctk.CTkFrame(self, fg_color="transparent")

        # ==========================================
        # FIXED EXPANDABLE BEIGE CANVAS SIDEBAR DOCK
        # ==========================================
        self.sidebar_drawer = ctk.CTkFrame(
            self.main_view_frame, width=75,
            fg_color="#f3eff7", border_width=2, border_color="#e2daeb",
            corner_radius=24
        )
        self.sidebar_drawer.pack(side="left", fill="y", padx=(15, 0), pady=15)
        self.sidebar_drawer.pack_propagate(False)

        # --- UPPER MENU OPTIONS ---
        self.menu_top_container = ctk.CTkFrame(self.sidebar_drawer, fg_color="transparent")
        self.menu_top_container.pack(fill="x", padx=15, pady=(20, 0))

        # Dynamic Burger/Expand Toggle Icon Trigger Button
        self.btn_menu_toggle = ctk.CTkButton(
            self.menu_top_container, text="≡", width=40, height=40,
            font=ctk.CTkFont(family="Comic Sans MS", size=14, weight="bold"),
            fg_color="transparent", text_color="#5e548e", hover_color="#e3dac9",
            command=self.toggle_sidebar_expansion
        )
        self.btn_menu_toggle.pack(anchor="w", padx=5, pady=(0, 15))

        # Title Branding Holder with Sparkles
        self.lbl_menu_title = ctk.CTkLabel(
            self.menu_top_container, text="✨",
            justify="left",
            font=ctk.CTkFont(family="Comic Sans MS", size=22, weight="bold"), text_color="#5e548e"
        )
        self.lbl_menu_title.pack(anchor="w", pady=(0, 25), padx=10)

        # Focus Hub Selection Anchor Buttons (Named explicitly to sync with the toggle expansion)
        self.btn_home = ctk.CTkButton(
            self.menu_top_container, text="🏠", font=ctk.CTkFont(family="Comic Sans MS", size=14),
            height=40, corner_radius=14, fg_color="transparent", text_color="#2b2d42", hover_color="#e5dfed",
            anchor="w", command=lambda: self.switch_content_tab_smoothly("focus")
        )
        self.btn_home.pack(fill="x", pady=2)

        self.btn_live_monitor = ctk.CTkButton(
            self.menu_top_container, text="📹",
            font=ctk.CTkFont(family="Comic Sans MS", size=14, weight="bold"),
            height=40, corner_radius=14, fg_color="#decfe6", text_color="#5e548e", hover_color="#decfe6",
            anchor="w", command=lambda: self.switch_content_tab_smoothly("live")
        )
        self.btn_live_monitor.pack(fill="x", pady=2)

        self.btn_sessions = ctk.CTkButton(
            self.menu_top_container, text="📖", font=ctk.CTkFont(family="Comic Sans MS", size=14),
            height=40, corner_radius=14, fg_color="transparent", text_color="#2b2d42", hover_color="#e5dfed",
            anchor="w", command=lambda: self.switch_content_tab_smoothly("sessions")
        )
        self.btn_sessions.pack(fill="x", pady=2)

        self.btn_history_log = ctk.CTkButton(
            self.menu_top_container, text="📊", font=ctk.CTkFont(family="Comic Sans MS", size=14),
            height=40, corner_radius=14, fg_color="transparent", text_color="#2b2d42", hover_color="#e5dfed",
            anchor="w", command=lambda: self.switch_content_tab_smoothly("history")
        )
        self.btn_history_log.pack(fill="x", pady=2)

        self.btn_alarm_config = ctk.CTkButton(
            self.menu_top_container, text="🔔", font=ctk.CTkFont(family="Comic Sans MS", size=14),
            height=40, corner_radius=14, fg_color="transparent", text_color="#2b2d42", hover_color="#e5dfed",
            anchor="w", command=lambda: self.switch_content_tab_smoothly("alarm")
        )
        self.btn_alarm_config.pack(fill="x", pady=2)

        self.btn_reports = ctk.CTkButton(
            self.menu_top_container, text="📂", font=ctk.CTkFont(family="Comic Sans MS", size=14),
            height=40, corner_radius=14, fg_color="transparent", text_color="#2b2d42", hover_color="#e5dfed",
            anchor="w", command=lambda: self.switch_content_tab_smoothly("reports")
        )
        self.btn_reports.pack(fill="x", pady=2)

        self.btn_settings = ctk.CTkButton(
            self.menu_top_container, text="⚙️", font=ctk.CTkFont(family="Comic Sans MS", size=14),
            height=40, corner_radius=14, fg_color="transparent", text_color="#2b2d42", hover_color="#e5dfed",
            anchor="w", command=lambda: self.switch_content_tab_smoothly("settings")
        )
        self.btn_settings.pack(fill="x", pady=2)

        self.btn_profile_view = ctk.CTkButton(
            self.menu_top_container, text="👤", font=ctk.CTkFont(family="Comic Sans MS", size=14),
            height=40, corner_radius=14, fg_color="transparent", text_color="#2b2d42", hover_color="#e5dfed",
            anchor="w", command=lambda: self.switch_content_tab_smoothly("profile")
        )
        self.btn_profile_view.pack(fill="x", pady=2)

        # --- LOWER CONTEXT SECTION (The Cute Plant Illustration Doodle Anchor) ---
        self.menu_bottom_container = ctk.CTkFrame(self.sidebar_drawer, fg_color="transparent")
        self.menu_bottom_container.pack(side="bottom", fill="x", padx=15, pady=20)

        self.lbl_plant_illustration = ctk.CTkLabel(
            self.menu_bottom_container, text="🪴",
            font=ctk.CTkFont(size=32)
        )
        self.lbl_plant_illustration.pack(pady=5)

        # ==========================================
        # RIGHT-SIDE MASTER CONTENT WORKSPACE
        # ==========================================
        self.right_content_pane = ctk.CTkFrame(self.main_view_frame, fg_color="transparent")
        self.right_content_pane.pack(side="right", fill="both", expand=True, padx=25, pady=10)

        # Sub-Frame 1: Focus Workspace View Panel Canvas
        self.main_canvas = ctk.CTkFrame(self.right_content_pane, fg_color="transparent")
        self.build_focus_hub_widgets()

        # Sub-Frame 2: History Analytics List Layout Canvas
        self.history_canvas = ctk.CTkFrame(self.right_content_pane, fg_color="transparent")
        self.build_history_ledger_widgets()

        # Sub-Frame 3: Real-Time Live Monitoring View linked to our multi-threaded loops
        self.live_monitoring_canvas = LiveMonitoringView(
            master=self.right_content_pane,
            stop_session_callback=self.start_button_clicked
        )
        self.alarm_canvas = AlarmSettingsView(master=self.right_content_pane, ui_parent=self)
        # Display defaults
        self.main_canvas.pack(fill="both", expand=True)
        self.current_visible_content_frame = self.main_canvas
        self.study_sessions_canvas = StudySessionsView(master=self.right_content_pane)
        self.reports_canvas = ReportsView(master=self.right_content_pane)
    # ========================================================
    # RIGHT CANVAS SECTIONAL COMPONENT GENERATORS
    # ========================================================
    def build_focus_hub_widgets(self):
        """Generates the cozy warm-beige handwritten study lounge arena frame."""
        self.status_bar_strip = ctk.CTkFrame(self.main_canvas, fg_color="transparent")
        self.status_bar_strip.pack(fill="x", anchor="e", pady=(10, 0), padx=10)

        self.lbl_cloud_doodle = ctk.CTkLabel(self.status_bar_strip, text="☁️✨", font=ctk.CTkFont(size=24), text_color="#bda0bc")
        self.lbl_cloud_doodle.pack(side="right")

        self.lbl_greeting = ctk.CTkLabel(
            self.main_canvas, text="Hey there, future achiever!",
            font=ctk.CTkFont(family="Comic Sans MS", size=16, slant="italic"), text_color="#e5989b"
        )
        self.lbl_greeting.pack(pady=(15, 0))

        self.logo_label = ctk.CTkLabel(
            self.main_canvas, text="Study Buddy",
            font=ctk.CTkFont(family="Comic Sans MS", size=56, weight="bold"), text_color="#5e548e"
        )
        self.logo_label.pack(pady=(2, 2))

        self.subtitle_label = ctk.CTkLabel(
            self.main_canvas, text="Let's make the day productive",
            font=ctk.CTkFont(family="Comic Sans MS", size=20), text_color="#4a4e69"
        )
        self.subtitle_label.pack(pady=(0, 25))

        self.action_button_frame = ctk.CTkFrame(self.main_canvas, fg_color="transparent")
        self.action_button_frame.pack(pady=15)

        self.btn_action_trigger = ctk.CTkButton(
            self.action_button_frame, text="Start Session  →",
            width=280, height=56, corner_radius=20,
            border_width=3, border_color="#5e548e",
            font=ctk.CTkFont(family="Comic Sans MS", size=18, weight="bold"),
            fg_color="#faf6ee", text_color="#5e548e", hover_color="#f3ece0",
            command=self.start_button_clicked
        )
        self.btn_action_trigger.pack()

        self.lbl_timer_clock = ctk.CTkLabel(
            self.main_canvas, text="50:00",
            font=ctk.CTkFont(family="Consolas", size=28, weight="bold"), text_color="#bda0bc"
        )
        self.lbl_timer_clock.pack(pady=5)
        self.lbl_timer_clock.pack_forget()

        self.bottom_dock = ctk.CTkFrame(self.main_canvas, fg_color="transparent")
        self.bottom_dock.pack(side="bottom", fill="x", pady=(0, 20))

        self.left_illustration_lbl = ctk.CTkLabel(self.bottom_dock, text="💡📚☕", font=ctk.CTkFont(size=26))
        self.left_illustration_lbl.pack(side="left", padx=25, anchor="s")

        self.quote_card = ctk.CTkFrame(
            self.bottom_dock, fg_color="#faf6ee",
            border_width=2, border_color="#bda0bc", corner_radius=14
        )
        self.quote_card.pack(side="left", expand=True, padx=10, pady=5)

        self.quote_text = ctk.CTkLabel(
            self.quote_card, text='“ Discipline today, success tomorrow.  💝 ”',
            font=ctk.CTkFont(family="Comic Sans MS", size=14), text_color="#4a4e69", padx=25, pady=16
        )
        self.quote_text.pack()

        self.right_illustration_lbl = ctk.CTkLabel(self.bottom_dock, text="✈️🪴⭐", font=ctk.CTkFont(size=26))
        self.right_illustration_lbl.pack(side="right", padx=25, anchor="s")

    def build_history_ledger_widgets(self):
        """Generates the embedded database ledger display sheet."""
        lbl_title = ctk.CTkLabel(
            self.history_canvas, text="Insights Ledger",
            font=ctk.CTkFont(family="Comic Sans MS", size=28, weight="bold"), text_color="#5e548e"
        )
        lbl_title.pack(anchor="w", pady=(20, 10), padx=20)

        self.txt_history_display = ctk.CTkTextbox(
            self.history_canvas, fg_color="#f5f2eb", text_color="#4a4e69",
            border_width=2, border_color="#c3b8a5", corner_radius=16,
            font=ctk.CTkFont(family="Consolas", size=13), padx=15, pady=15
        )
        self.txt_history_display.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # ========================================================
    # NATIVE SAME-PAGE FLUID TRANSITION NAVIGATION ENGINE
    # ========================================================
    def switch_content_tab_smoothly(self, target_tab):
        """Swaps view canvas layers dynamically and syncs active custom button highlight states."""
        if target_tab == self.active_tab and self.current_visible_content_frame.winfo_manager() != "":
            return

        self.active_tab = target_tab

        if self.current_visible_content_frame:
            self.current_visible_content_frame.pack_forget()

        # Completely reset all navigation buttons back to light transparent text choices
        buttons_list = [
            self.btn_home, self.btn_live_monitor, self.btn_sessions,
            self.btn_history_log, self.btn_alarm_config, self.btn_reports,
            self.btn_settings, self.btn_profile_view
        ]
        for btn in buttons_list:
            btn.configure(fg_color="transparent", text_color="#2b2d42", font=ctk.CTkFont(family="Comic Sans MS", size=14))

        # Dynamically evaluate selection target and apply soft lavender highlight pill tracking boxes
        if target_tab == "focus":
            self.btn_home.configure(fg_color="#decfe6", text_color="#5e548e", font=ctk.CTkFont(family="Comic Sans MS", size=14, weight="bold"))
            self.main_canvas.pack(fill="both", expand=True)
            self.current_visible_content_frame = self.main_canvas

        elif target_tab == "live":
            self.btn_live_monitor.configure(fg_color="#decfe6", text_color="#5e548e",
                                            font=ctk.CTkFont(family="Comic Sans MS", size=14, weight="bold"))
            self.live_monitoring_canvas.pack(fill="both", expand=True)
            self.current_visible_content_frame = self.live_monitoring_canvas
            # Simply update the state engine cleanly
            self.live_monitoring_canvas.update_ui_state(self.session_running)
        elif target_tab == "sessions":
            # Highlight sidebar menu button
            self.btn_sessions.configure(fg_color="#decfe6", text_color="#5e548e",
                                     font=ctk.CTkFont(family="Comic Sans MS", size=14, weight="bold"))
            # Show the new beautiful frame canvas layout workspace
            self.study_sessions_canvas.pack(fill="both", expand=True)
            self.current_visible_content_frame = self.study_sessions_canvas
        elif target_tab == "history":
            self.btn_history_log.configure(fg_color="#decfe6", text_color="#5e548e", font=ctk.CTkFont(family="Comic Sans MS", size=14, weight="bold"))
            self.history_canvas.pack(fill="both", expand=True)
            self.current_visible_content_frame = self.history_canvas
            self.load_database_history_into_ui()

        elif target_tab == "alarm":
            self.btn_alarm_config.configure(fg_color="#decfe6", text_color="#5e548e",
                                            font=ctk.CTkFont(family="Comic Sans MS", size=14, weight="bold"))

            # --- MAKE SURE THESE ARGS ARE EXACTLY HERE ---
            self.alarm_canvas.pack(fill="both", expand=True)
            self.current_visible_content_frame = self.alarm_canvas

        elif target_tab in ["reports", "report"]:
            self.btn_reports.configure(fg_color="#decfe6", text_color="#5e548e",
                                       font=ctk.CTkFont(family="Comic Sans MS", size=14, weight="bold"))
            self.reports_canvas.pack(fill="both", expand=True)
            self.current_visible_content_frame = self.reports_canvas

        else:
            target_btn_map = {
                "reports": self.btn_reports, "settings": self.btn_settings, "profile": self.btn_profile_view
            }
            active_btn = target_btn_map.get(target_tab)
            if active_btn:
                active_btn.configure(fg_color="#decfe6", text_color="#5e548e", font=ctk.CTkFont(family="Comic Sans MS", size=14, weight="bold"))

            self.history_canvas.pack(fill="both", expand=True)
            self.current_visible_content_frame = self.history_canvas

            self.txt_history_display.configure(state="normal")
            self.txt_history_display.delete("1.0", "end")
            self.txt_history_display.insert("end", f"✨ {target_tab.capitalize()} View Core Block Container\n\nExtended user interface properties coming soon to this ledger layer...")
            self.txt_history_display.configure(state="disabled")

    def load_database_history_into_ui(self):
        """Connects to SQLite database files and reads records directly into dashboard display lists."""
        self.txt_history_display.configure(state="normal")
        self.txt_history_display.delete("1.0", "end")

        header = f" {'INDEX':<12}{'TIMESTAMP RECORD':<20}{'DURATION COUNTER':<22}{'INCIDENTS LOGGED':<15}\n"
        divider = "─" * 70 + "\n"
        self.txt_history_display.insert("end", header + divider)

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, session_date, total_study_seconds, drowsy_incidents_count FROM session_history ORDER BY id DESC")
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                self.txt_history_display.insert("end", "\n No entries logged inside database schema files yet.")
            else:
                for row in rows:
                    session_id, s_date, total_secs, alert_count = row
                    mins, secs = divmod(total_secs, 60)
                    time_str = f"{mins}m {secs}s"
                    row_string = f" #{session_id:<11}{s_date:<20}{time_str:<22}{alert_count:<15}\n"
                    self.txt_history_display.insert("end", row_string)
        except Exception as e:
            self.txt_history_display.insert("end", f"IO Exception connecting to SQLite database file systems: {str(e)}")

        self.txt_history_display.configure(state="disabled")

    # ========================================================
    # OPERATIONAL AI BUSINESS CALCULATIONS LOGIC
    # ========================================================
    def start_button_clicked(self):
        if not self.session_running:
            self.session_running = True
            self.last_clock_tick = time.time()
            self.lbl_timer_clock.pack(pady=5)

            # Jump cleanly to live video panel loop upon tracking initialization
            self.switch_content_tab_smoothly("live")

            self.btn_action_trigger.configure(text="Stop Session  ■", fg_color="#faf6ee", text_color="#ff4d6d", border_color="#ff4d6d")

            self.ai_thread = threading.Thread(target=self.worker_thread_task, daemon=True)
            self.ai_thread.start()

        else:
            self.session_running = False
            actual_seconds_studied = self.total_session_seconds - self.study_seconds_left
            if actual_seconds_studied < 0: actual_seconds_studied = 0

            if actual_seconds_studied > 0:
                log_study_session(actual_seconds_studied, self.drowsy_alerts_count)

            # ─── RESET THE INTERNAL TIMER TRACKERS ───
            self.study_seconds_left = config.STUDY_MINUTES * 60

            # ─── UPDATE AND RESET UI LABELS INSTANTLY ───
            # 1. Reset the main focus hub timer display
            self.lbl_timer_clock.configure(text="50:00")
            self.lbl_timer_clock.pack_forget()

            # 2. Reset the live monitoring session timer clock view cleanly
            if hasattr(self, 'live_monitoring_canvas'):
                self.live_monitoring_canvas.lbl_live_session_clock.configure(text="00:50:00")

            self.drowsy_alerts_count = 0
            self.was_drowsy_last_frame = False

            # Drop back down to cozy entry hub upon execution stop
            self.switch_content_tab_smoothly("focus")
            self.btn_action_trigger.configure(text="Start Session  →", fg_color="#faf6ee", text_color="#5e548e",
                                              border_color="#5e548e")
    def worker_thread_task(self):
        def focus_signal():
            if self.session_running: self.status_queue.put("FOCUS")
        def drowsy_signal():
            if self.session_running: self.status_queue.put("DROWSY")
        def check_if_stopped():
            return not self.session_running

        run_eye_tracker(
            on_focused_callback=focus_signal,
            on_drowsy_callback=drowsy_signal,
            stop_check_callback=check_if_stopped,
            frame_callback=self.process_incoming_camera_frame
        )

    def update_timer_loop(self):
        current_time = time.time()
        is_focused = True

        try:
            while True:
                status_update = self.status_queue.get_nowait()
                if not self.session_running:
                    break

                if status_update == "FOCUS":
                    self.live_monitoring_canvas.lbl_live_eye_val.configure(text="OPEN", text_color="#2a9d8f")
                    self.live_monitoring_canvas.lbl_live_focus_val.configure(text="85%", text_color="#5e548e")
                    self.live_monitoring_canvas.lbl_live_posture_val.configure(text="Good", text_color="#2a9d8f")
                    self.quote_text.configure(text='“ Keep going! You are doing amazing. ✨ ”', text_color="#5e548e")
                    self.was_drowsy_last_frame = False
                elif status_update == "DROWSY":
                    self.live_monitoring_canvas.lbl_live_eye_val.configure(text="CLOSED 🚨", text_color="#ef4444")
                    self.live_monitoring_canvas.lbl_live_focus_val.configure(text="20%", text_color="#ef4444")
                    self.live_monitoring_canvas.lbl_live_posture_val.configure(text="Drowsy", text_color="#ef4444")
                    self.quote_text.configure(text='“ Hey, your eyes look tired. Take a deep breath! ☕ ”', text_color="#ff4d6d")
                    is_focused = False

                    if not self.was_drowsy_last_frame:
                        self.drowsy_alerts_count += 1
                        self.was_drowsy_last_frame = True
        except queue.Empty:
            pass

        if self.session_running:
            if is_focused:
                if current_time - self.last_clock_tick >= 1.0:
                    self.study_seconds_left -= 1
                    self.last_clock_tick = current_time
            else:
                self.last_clock_tick = current_time

            if self.study_seconds_left <= 0:
                self.start_button_clicked()
                return

            mins, secs = divmod(max(0, self.study_seconds_left), 60)
            self.lbl_timer_clock.configure(text=f"{mins:02d}:{secs:02d}")
            self.live_monitoring_canvas.lbl_live_session_clock.configure(text=f"00:{mins:02d}:{secs:02d}")
        if self.winfo_exists():
            self.after(100, self.update_timer_loop)

    def toggle_sidebar_expansion(self):
        """Animates expanding/collapsing the sidebar and updates text label string properties instantly."""
        if not self.sidebar_expanded:
            self.sidebar_expanded = True
            self.sidebar_drawer.configure(width=260)

            self.btn_menu_toggle.configure(text="✕")
            self.lbl_menu_title.configure(text="✨ Study\n    Buddy ✧")
            self.btn_home.configure(text="🏠   Home")
            self.btn_live_monitor.configure(text="📹   Live Monitoring")
            self.btn_sessions.configure(text="📖   Study Sessions")
            self.btn_history_log.configure(text="📊   Analytics")
            self.btn_alarm_config.configure(text="🔔   Alarm Settings")
            self.btn_reports.configure(text="📂   Reports")
            self.btn_settings.configure(text="⚙️   Settings")
            self.btn_profile_view.configure(text="👤   Profile")
            self.lbl_plant_illustration.configure(text="🪴")
        else:
            self.sidebar_expanded = False
            self.sidebar_drawer.configure(width=75)

            self.btn_menu_toggle.configure(text="≡")
            self.lbl_menu_title.configure(text="✨")
            self.btn_home.configure(text="🏠")
            self.btn_live_monitor.configure(text="📹")
            self.btn_sessions.configure(text="📖")
            self.btn_history_log.configure(text="📊")
            self.btn_alarm_config.configure(text="🔔")
            self.btn_reports.configure(text="📂")
            self.btn_settings.configure(text="⚙️")
            self.btn_profile_view.configure(text="👤")
            self.lbl_plant_illustration.configure(text="🪴")

    def process_incoming_camera_frame(self, cv_frame):
        """Converts raw OpenCV matrix streams to structural Tkinter UI photo textures safely."""
        from PIL import Image, ImageTk
        import cv2

        if not self.session_running:
            return

        try:
            resized_frame = cv2.resize(cv_frame, (520, 360))
            rgb_image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_image)

            # Attached directly to self to stop Garbage Collection destruction loop
            self.ui_photo_texture = ImageTk.PhotoImage(image=pil_img)

            self.live_monitoring_canvas.live_video_label.configure(image=self.ui_photo_texture, text="")
            self.live_monitoring_canvas.live_video_label.image = self.ui_photo_texture

        except Exception as e:
            print(f"[UI STREAM ERROR] Failed painting video matrix: {str(e)}")

    def on_closing(self):
        """Cleanly stops background loops and exits the application without Tkinter after errors."""
        # 1. Flag session as stopped to break background worker & timer loops
        self.session_running = False

        try:
            self.withdraw()  # Hide window immediately
            self.quit()  # Exit Tcl/Tk main loop cleanly
            self.destroy()  # Destroy widgets
        except Exception:
            pass

if __name__ == "__main__":
    app = StudyGuardianUI()
    app.mainloop()