import sqlite3
from datetime import date

from app.schedule.repository import (
    get_slots_for_doctor_on_date,
    generate_time_slots,
)


DB_PATH = "schedule.db"


def _duration_for(doctor_name: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT duration_min FROM doctor_duration WHERE doctor_name = ?",
        (doctor_name,),
    ).fetchone()
    conn.close()
    return int(row[0]) if row else 20


def build_all_slots(doctor_name: str, target_date: date) -> list[dict]:
    duration = _duration_for(doctor_name)
    shifts = get_slots_for_doctor_on_date(doctor_name, target_date)
    result = []
    for s in shifts:
        for t in generate_time_slots(s["start_time"], s["end_time"], duration):
            result.append({
                "scheduled_at": f"{target_date.strftime('%d.%m.%Y')} {t}",
                "time": t,
                "cabinet": s["cabinet"],
                "shift": s["shift"],
            })
    return result


def filter_busy(all_slots: list[dict], busy: set[str]) -> list[dict]:
    return [s for s in all_slots if s["scheduled_at"] not in busy]
