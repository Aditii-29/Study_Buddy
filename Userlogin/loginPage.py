from logging import root
from tkinter import*
import customtkinter as ctk
from PIL import ImageTk
from matplotlib.pyplot import title


class loginPage(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Study Buddy")
        self.geometry("1020x660")
        self.resizable(False, False)

        ctk.set_appearance_mode("light")
        self.configure(fg_color="#faf6ee")
    def create_login_screen_layout(self):
        self.login_view_frame = ctk.CTkFrame(self, fg_color="transparent")

        # Welcoming Header
        lbl_welcome_title = ctk.CTkLabel(
            self.login_view_frame, text="Welcome, Study Buddy",
            font=ctk.CTkFont(family="Comic Sans MS", size=38, weight="bold"), text_color="#5e548e"
        )
        lbl_welcome_title.pack(pady=(120, 10))

        lbl_welcome_sub = ctk.CTkLabel(
            self.login_view_frame, text="Enter your workspace credentials to join your desk.",
            font=ctk.CTkFont(family="Comic Sans MS", size=15), text_color="#4a4e69"
        )
        lbl_welcome_sub.pack(pady=(0, 40))

        # Input Forms Matrix Wrapper
        form_frame = ctk.CTkFrame(self.login_view_frame, fg_color="transparent")
        form_frame.pack(pady=10)

        self.entry_username = ctk.CTkEntry(
            form_frame, placeholder_text="Username", width=300, height=45, corner_radius=12,
            border_width=2, border_color="#5e548e", fg_color="#faf6ee", text_color="#4a4e69",
            font=ctk.CTkFont(family="Comic Sans MS", size=13)
        )
        self.entry_username.pack(pady=10)

        self.entry_password = ctk.CTkEntry(
            form_frame, placeholder_text="Password", show="*", width=300, height=45, corner_radius=12,
            border_width=2, border_color="#5e548e", fg_color="#faf6ee", text_color="#4a4e69",
            font=ctk.CTkFont(family="Comic Sans MS", size=13)
        )
        self.entry_password.pack(pady=10)

        # Login Action Trigger Button
        btn_login_trigger = ctk.CTkButton(
            self.login_view_frame, text="Enter Workspace  →",
            width=300, height=50, corner_radius=16,
            font=ctk.CTkFont(family="Comic Sans MS", size=16, weight="bold"),
            fg_color="#5e548e", text_color="#ffffff", hover_color="#4d4475",
            border_width=2, border_color="#5e548e",
            command=self.authenticate_and_launch_dashboard
        )
        btn_login_trigger.pack(pady=30)

    def show_login_screen(self):
        """Mounts the login window to full view."""
        if self.login_view_frame.pack_forget():
            self.main_view_frame.pack_forget()
        self.login_view_frame.pack(fill="both", expand=True)

    def authenticate_and_launch_dashboard(self):
        """Verifies access input parameters and cleanly transitions into workspace layout."""
        username = self.entry_username.get().strip()
        if username == "":
            username = "Scholar"

        print(f"[AUTH SYSTEM] Access Granted for profile target: {username}")

        # Unpack Login, build, and deploy the main dual-column dashboard
        self.login_view_frame.pack_forget()
        self.create_main_dashboard_layout()
        self.main_view_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = loginPage()
    app.mainloop()