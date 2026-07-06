# main.py
import sys
import os

# Initialize database schemas before booting user interface loops
from database.db_manager import initialize_database
from gui.dashboard import StudyGuardianUI


def main():
    print("[SYSTEM INITIALIZATION] Booting Study Buddy Suite...")

    # Ensure local database files and tables exist cleanly on startup
    initialize_database()

    # Launch the master multi-view user interface canvas track
    app = StudyGuardianUI()
    app.mainloop()


if __name__ == "__main__":
    main()