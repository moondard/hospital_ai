import sqlite3
from datetime import date, datetime, timedelta


DB_PATH = "schedule.db"


def get_slots_for_doctor_on_date(doctor_name: str, target_date: date) -> list[dict]:
    dow = target_date.isoweekday()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM slots WHERE doctor_name = ? AND day_of_week = ?",
        (doctor_name, dow),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def generate_time_slots(start: str, end: str, step_min: int = 20) -> list[str]:
    fmt = "%H:%M"
    t = datetime.strptime(start, fmt)
    end_t = datetime.strptime(end, fmt)
    result = []
    while t + timedelta(minutes=step_min) <= end_t:
        result.append(t.strftime(fmt))
        t += timedelta(minutes=step_min)
    return result
