# gui/register_view.py
import tkinter as tk
from tkinter import messagebox
from Engine.auth_backend import register_user

class RegisterView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#F4F6F9")

        # --- UI LAYOUT DESIGN ELEMENTS ---
        title_label = tk.Label(
            self, text="Create Account", font=("Helvetica", 24, "bold"),
            bg="#F4F6F9", fg="#2C3E50"
        )
        title_label.pack(pady=(30, 15))

        # Username Widget
        user_label = tk.Label(self, text="Username", font=("Helvetica", 11), bg="#F4F6F9", fg="#7F8C8D")
        user_label.pack(anchor="w", padx=50, pady=(10, 2))
        self.username_entry = tk.Entry(self, font=("Helvetica", 12), width=30, bd=1, relief="solid")
        self.username_entry.pack(padx=50, pady=5)

        # Email Widget
        email_label = tk.Label(self, text="Email Address", font=("Helvetica", 11), bg="#F4F6F9", fg="#7F8C8D")
        email_label.pack(anchor="w", padx=50, pady=(10, 2))
        self.email_entry = tk.Entry(self, font=("Helvetica", 12), width=30, bd=1, relief="solid")
        self.email_entry.pack(padx=50, pady=5)

        # Password Widget
        password_label = tk.Label(self, text="Password (Min 6 Characters)", font=("Helvetica", 11), bg="#F4F6F9", fg="#7F8C8D")
        password_label.pack(anchor="w", padx=50, pady=(10, 2))
        self.password_entry = tk.Entry(self, font=("Helvetica", 12), width=30, bd=1, relief="solid", show="*")
        self.password_entry.pack(padx=50, pady=5)

        # --- SUBMISSION ACTION SELECTIONS ---
        register_btn = tk.Button(
            self, text="Register System Account", font=("Helvetica", 12, "bold"),
            bg="#2ECC71", fg="white", width=28, bd=0, cursor="hand2",
            command=self.handle_final_registration
        )
        register_btn.pack(padx=50, pady=25)

        switch_frame_btn = tk.Button(
            self, text="Already registered? Sign In instead", font=("Helvetica", 10, "underline"),
            bg="#F4F6F9", fg="#2980B9", bd=0, cursor="hand2",
            command=lambda: controller.show_frame("LoginView")
        )
        switch_frame_btn.pack(pady=5)

    def handle_final_registration(self):
        """Validates entry values and populates MongoDB records securely."""
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        # Run Backend Hashing and Insertion Engine Pipeline
        success, message = register_user(username, email, password)

        if success:
            messagebox.showinfo("Success", message)
            self.clear_fields()
            # Redirect the user to the active login frame to sign in
            self.controller.show_frame("LoginView")
        else:
            messagebox.showerror("Registration Error", message)

    def clear_fields(self):
        """Wipes strings inside entries dynamically."""
        self.username_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)