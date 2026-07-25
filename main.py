# main.py
import sys
import os

# Launch the master multi-view user interface canvas track
from gui.dashboard import StudyGuardianUI


def main():
    print("[SYSTEM INITIALIZATION] Booting Study Buddy Suite...")
    print("[DATABASE] Connecting to MongoDB Server backend layout...")

    # Launch the user interface canvas directly
    app = StudyGuardianUI()
    app.mainloop()


if __name__ == "__main__":
    main()