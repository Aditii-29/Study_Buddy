import sqlite3
import os

from datetime import datetime,timedelta

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
    return text


def get_study_session_metrics():
    """Calculates performance indicators directly from the session tracking ledger."""
    metrics = {
        "today_seconds": 0,
        "total_seconds": 0,
        "avg_focus": 85,  # Default fallback index
        "streak_days": 0,
        "recent_sessions": []
    }

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Fetch historical entries
        cursor.execute("""
            SELECT session_date, total_study_seconds, drowsy_incidents_count 
            FROM session_history 
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()

        if not rows:
            conn.close()
            return metrics

        # SQLite's CURRENT_DATE format is YYYY-MM-DD
        today_str = datetime.now().strftime("%Y-%m-%d")
        total_seconds = 0
        today_seconds = 0
        focus_scores = []
        unique_dates = set()

        # 2. Compute aggregate values
        for row in rows:
            s_date, total_secs, drowsy_count = row
            total_seconds += total_secs

            # Extract just the date part in case timestamp details creep in
            clean_date_str = s_date.split()[0] if s_date else ""
            if clean_date_str:
                unique_dates.add(clean_date_str)

            if clean_date_str == today_str:
                today_seconds += total_secs

            # Focus performance calculation formula: 100% baseline - 5% per alert (floor at 20%)
            calculated_focus = max(20, 100 - (drowsy_count * 5))
            focus_scores.append(calculated_focus)

        metrics["total_seconds"] = total_seconds
        metrics["today_seconds"] = today_seconds
        metrics["avg_focus"] = int(sum(focus_scores) / len(focus_scores)) if focus_scores else 85

        # 3. Calculate Daily Streak Length
        streak = 0
        check_date = datetime.now()

        # If they haven't studied today, check if they studied yesterday to maintain the streak
        if today_str not in unique_dates:
            check_date -= timedelta(days=1)

        while True:
            date_str = check_date.strftime("%Y-%m-%d")
            if date_str in unique_dates:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        metrics["streak_days"] = streak

        # 4. Format the 5 most recent sessions for the card list view strips
        cursor.execute("""
            SELECT id, session_date, total_study_seconds, drowsy_incidents_count 
            FROM session_history 
            ORDER BY id DESC LIMIT 5
        """)
        recent_rows = cursor.fetchall()

        for r in recent_rows:
            s_id, r_date, r_secs, r_drowsy = r
            r_mins, _ = divmod(r_secs, 60)
            r_focus = max(20, 100 - (r_drowsy * 5))

            # Format raw 'YYYY-MM-DD' to beautiful cozy text 'DD B, YYYY' (e.g., 20 July, 2026)
            try:
                parsed_date = datetime.strptime(r_date.split()[0], "%Y-%m-%d")
                formatted_date = parsed_date.strftime("%d %B, %Y")
            except:
                formatted_date = r_date

            metrics["recent_sessions"].append({
                "title": f"Study Session #{s_id}",
                "date": formatted_date,
                "time": f"{r_mins}m" if r_mins > 0 else f"{r_secs}s",
                "focus": f"{r_focus}%"
            })

        conn.close()
    except Exception as e:
        print(f"[DB METRICS BACKEND ERROR] {str(e)}")

    return metrics
if __name__ == "__main__":
    # This forces the file to run the code when you right-click and play it directly
    initialize_database()