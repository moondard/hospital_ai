import httpx
from app.config import settings


class CRMError(Exception):
    """Ошибка CRM API с кодом и сообщением из ответа."""

    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(f"[{status_code} {code}] {message}")


class CRMClient:
    def __init__(self):
        self.base = settings.crm_base_url
        self.headers = {"Authorization": f"Bearer {settings.crm_token}"}

    async def _request(self, method: str, path: str, **kwargs) -> dict | list:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.request(
                method, f"{self.base}{path}", headers=self.headers, **kwargs
            )
            if r.status_code >= 400:
                try:
                    body = r.json()
                    raise CRMError(r.status_code, body.get("code", "?"),
                                   body.get("message", "?"))
                except ValueError:
                    raise CRMError(r.status_code, "?", r.text)
            return r.json()

    async def list_doctors(self, specialty: str | None = None) -> list[dict]:
        params = {}
        if specialty:
            params["specialty"] = specialty
        return await self._request("GET", "/doctors", params=params)

    async def create_client(self, last_name: str, first_name: str,
                            birth_date: str, middle_name: str | None = None,
                            comment: str | None = None) -> dict:
        body = {
            "last_name": last_name,
            "first_name": first_name,
            "birth_date": birth_date,
        }
        if middle_name:
            body["middle_name"] = middle_name
        if comment:
            body["comment"] = comment
        return await self._request("POST", "/clients", json=body)

    async def find_clients(self, last_name: str, first_name: str,
                           birth_date: str) -> list[dict]:
        params = {
            "last_name": last_name,
            "first_name": first_name,
            "birth_date": birth_date,
        }
        return await self._request("GET", "/clients", params=params)

    async def list_visits(self, doctor_id: int | None = None,
                          client_id: int | None = None,
                          status: str | None = None,
                          date_from: str | None = None,
                          date_to: str | None = None) -> list[dict]:
        params = {}
        if doctor_id is not None:
            params["doctor_id"] = str(doctor_id)
        if client_id is not None:
            params["client_id"] = str(client_id)
        if status:
            params["status"] = status
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        return await self._request("GET", "/visits", params=params)

    async def create_visit(self, client_id: int, doctor_id: int,
                           scheduled_at: str) -> dict:
        body = {
            "client_id": client_id,
            "doctor_id": doctor_id,
            "scheduled_at": scheduled_at,
        }
        return await self._request("POST", "/visits", json=body)

    async def update_visit(self, visit_id: int, **fields) -> dict:
        return await self._request("PATCH", f"/visits/{visit_id}", json=fields)
