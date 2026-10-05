import sqlite3

import pandas as pd


DB_PATH = "schedule.db"


def load_schedule(xlsx_path: str, db_path: str = DB_PATH) -> int:
    df = pd.read_excel(xlsx_path, sheet_name="Слоты (для БД)")

    df = df.rename(columns={
        "ФИО": "doctor_name",
        "Специальность": "specialty",
        "Кабинет": "cabinet",
        "day_of_week (1=Пн)": "day_of_week",
        "День": "day_name",
        "Смена": "shift",
        "Начало": "start_time",
        "Конец": "end_time",
    })

    cols = ["doctor_id", "doctor_name", "specialty", "cabinet",
            "day_of_week", "day_name", "shift", "start_time", "end_time"]
    df = df[cols].dropna(subset=["doctor_id"])

    df["doctor_id"] = df["doctor_id"].astype(int)
    df["day_of_week"] = df["day_of_week"].astype(int)
    df["cabinet"] = df["cabinet"].astype(int)

    conn = sqlite3.connect(db_path)
    df.to_sql("slots", conn, if_exists="replace", index=False)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_slots_name ON slots(doctor_name)")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_slots_dow ON slots(day_of_week)")
    conn.commit()
    conn.close()

    return len(df)


def load_durations(xlsx_path: str, db_path: str = DB_PATH) -> int:
    df = pd.read_excel(xlsx_path, sheet_name="По врачам")

    df = df.rename(columns={
        "ФИО": "doctor_name",
        "Специальность": "specialty",
        "Длит. приёма, мин": "duration_min",
    })

    df = df[["doctor_name", "specialty", "duration_min"]].dropna(
        subset=["doctor_name", "duration_min"]
    )
    df["duration_min"] = df["duration_min"].astype(int)

    conn = sqlite3.connect(db_path)
    df.to_sql("doctor_duration", conn, if_exists="replace", index=False)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_duration_name ON doctor_duration(doctor_name)"
    )
    conn.commit()
    conn.close()

    return len(df)


if __name__ == "__main__":
    n_slots = load_schedule("data/raspisanie.xlsx")
    n_durations = load_durations("data/raspisanie.xlsx")
    print(f"Загружено слотов: {n_slots}")
    print(f"Загружено длительностей: {n_durations}")
