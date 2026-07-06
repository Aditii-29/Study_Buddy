# Engine/analytics.py

def calculate_focus_score(total_seconds, alert_count):
    """Calculates an efficiency score out of 100 based on session behavior."""
    if total_seconds <= 0:
        return 100

    # Penalize focus rating based on drowsiness incident frequency
    penalty_factor = 30  # Adjusts severity weight of alert triggers
    deduction = (alert_count * penalty_factor) / (total_seconds / 60)
    score = max(0, min(100, 100 - deduction))
    return round(score, 1)