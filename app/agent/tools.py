from datetime import datetime

from app.crm.client import CRMClient
from app.schedule.available import build_all_slots, filter_busy


crm = CRMClient()

DATE_FMT = "%d.%m.%Y"


async def find_doctor(specialty: str) -> list[dict]:
    doctors = await crm.list_doctors(specialty=specialty)
    return [
        {"id": d["id"], "full_name": d["full_name"],
         "specialty": d["specialty"]}
        for d in doctors if d["is_active"]
    ]


async def create_client(last_name: str, first_name: str, birth_date: str,
                        middle_name: str | None = None) -> dict:
    return await crm.create_client(
        last_name=last_name, first_name=first_name,
        birth_date=birth_date, middle_name=middle_name,
    )


async def get_slots(doctor_name: str, date_str: str) -> list[dict]:
    target = datetime.strptime(date_str, DATE_FMT).date()

    all_slots = build_all_slots(doctor_name, target)
    if not all_slots:
        return []

    doctors = await crm.list_doctors()
    doctor = next(
        (d for d in doctors if d["full_name"] == doctor_name), None
    )
    if not doctor:
        return all_slots

    visits = await crm.list_visits(
        doctor_id=doctor["id"],
        status="Запланирована",
        date_from=date_str,
        date_to=date_str,
    )
    busy = {v["scheduled_at"] for v in visits}

    return filter_busy(all_slots, busy)


async def book_appointment(client_id: int, doctor_id: int,
                           scheduled_at: str) -> dict:
    return await crm.create_visit(
        client_id=client_id, doctor_id=doctor_id,
        scheduled_at=scheduled_at,
    )


async def list_appointments(client_id: int) -> list[dict]:
    visits = await crm.list_visits(client_id=client_id)
    return [
        {
            "id": v["id"],
            "doctor_name": v["doctor"]["full_name"],
            "specialty": v["doctor"]["specialty"],
            "scheduled_at": v["scheduled_at"],
            "status": v["status"],
        }
        for v in visits
    ]


async def cancel_appointment(visit_id: int) -> dict:
    return await crm.update_visit(visit_id, status="Отменена")
