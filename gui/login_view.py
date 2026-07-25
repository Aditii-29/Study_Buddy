# gui/login_view.py
import tkinter as tk
from tkinter import messagebox
from Engine.auth_backend import login_user

class LoginView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F4F6F9")

        # --- UI LAYOUT DESIGN ELEMENTS ---
        title_label = tk.Label(
            self, text="Study Buddy Portal", font=("Helvetica", 24, "bold"),
            bg="#F4F6F9", fg="#2C3E50"
        )
        title_label.pack(pady=(40, 20))

        # Email Entry Components
        email_label = tk.Label(self, text="Email Address", font=("Helvetica", 11), bg="#F4F6F9", fg="#7F8C8D")
        email_label.pack(anchor="w", padx=50, pady=(10, 2))
        self.email_entry = tk.Entry(self, font=("Helvetica", 12), width=30, bd=1, relief="solid")
        self.email_entry.pack(padx=50, pady=5)

        # Password Entry Components
        password_label = tk.Label(self, text="Password", font=("Helvetica", 11), bg="#F4F6F9", fg="#7F8C8D")
        password_label.pack(anchor="w", padx=50, pady=(10, 2))
        self.password_entry = tk.Entry(self, font=("Helvetica", 12), width=30, bd=1, relief="solid", show="*")
        self.password_entry.pack(padx=50, pady=5)

        # --- ACTION INTERACTION BUTTONS ---
        login_btn = tk.Button(
            self, text="Sign In", font=("Helvetica", 12, "bold"),
            bg="#3498DB", fg="white", width=28, bd=0, cursor="hand2",
            command=self.handle_login_click
        )
        login_btn.pack(padx=50, pady=25)

        switch_frame_btn = tk.Button(
            self, text="Don't have an account? Register here", font=("Helvetica", 10, "underline"),
            bg="#F4F6F9", fg="#2980B9", bd=0, cursor="hand2",
            command=lambda: controller.show_frame("RegisterView")
        )
        switch_frame_btn.pack(pady=10)

    def handle_login_click(self):
        """Extracts data values from inputs and verifies credentials via the backend."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        # Run Backend Verification Engine
        success, result = login_user(email, password)

        if success:
            messagebox.showinfo("Welcome", f"Access Granted! Welcome back, {result}.")
            # Reset entry fields cleanly for next usage session cycle
            self.clear_fields()
            # Redirect main execution flow into your main dashboard frame
            self.controller.navigate_to_dashboard()
        else:
            # Display database or layout constraint validation reasoning error text
            messagebox.showerror("Login Failed", result)

    def clear_fields(self):
        """Resets the content entry inputs cleanly."""
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)