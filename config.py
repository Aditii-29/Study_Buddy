# config.py
import os

# Base directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- AI & Computer Vision Settings ---
EAR_THRESHOLD = 0.22             # Below this means eyes are closed
EYE_CLOSED_LIMIT_SECONDS = 3.0   # Time limit before alarm rings

# --- Audio Settings ---
ALARM_FREQUENCY = 2000           # High pitch alert (Hz)
ALARM_DURATION_MS = 400          # Beep duration (milliseconds)

#Pomodoro settings(In minutes)
STUDY_MINUTES=50
BREAK_MINUTES=1
# --- Database Settings ---
DB_PATH = os.path.join(BASE_DIR, "database", "study_history.db")

# --- UI Themes & Visuals ---
APP_THEME = "dark"               # Modern dark mode look
COLOR_THEME = "blue"             # Core branding color