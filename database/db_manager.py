# database/db_manager.py
import sqlite3
import os

# Define path to ensure the database file is saved right inside the database folder
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "study_history.db")


def initialize_database():
    """Creates the SQLite database file and the session tracking table if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the schema table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_date TEXT DEFAULT CURRENT_DATE,
            total_study_seconds INTEGER,
            drowsy_incidents_count INTEGER
        )
    ''')

    conn.commit()
    conn.close()
    print(font_style_check("[DATABASE] SQLite engine initialized and schema verified layout."))


def log_study_session(seconds_studied, drowsy_count):
    """Inserts a completed study session record into the local storage file."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO session_history (total_study_seconds, drowsy_incidents_count)
        VALUES (?, ?)
    ''', (seconds_studied, drowsy_count))

    conn.commit()
    conn.close()
    print(f"\n[DATABASE] Session logged successfully! Saved: {seconds_studied}s studied, {drowsy_count} alerts.")


def font_style_check(text):
    return text  # Simple helper wrapper
# Add this at the very bottom of database/db_manager.py
if __name__ == "__main__":
    # This forces the file to run the code when you right-click and play it directly
    initialize_database()