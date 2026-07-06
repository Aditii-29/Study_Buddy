# gui/components.py
import customtkinter as ctk

class CozySketchCard(ctk.CTkFrame):
    """A reusable hand-drawn style container frame for the Study Buddy theme."""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color="#faf6ee",       # Warm beige inner card canvas
            border_width=2,           # Emphasized sketch line weight
            border_color="#bda0bc",   # Pastel lavender outline border
            corner_radius=14,         # Curved boundary arcs
            **kwargs
        )