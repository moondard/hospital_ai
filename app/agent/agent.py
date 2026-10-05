import json
from datetime import datetime, timedelta, timezone

from ollama import chat

from app.agent import tools
from app.agent.prompts import SYSTEM_PROMPT
from app.config import settings


STAND_TZ = timezone(timedelta(hours=4))

TOOLS = [
    tools.find_doctor,
    tools.create_client,
    tools.get_slots,
    tools.book_appointment,
    tools.list_appointments,
    tools.cancel_appointment,
]


class Agent:
    def __init__(self):
        today = datetime.now(STAND_TZ).strftime("%d.%m.%Y")
        self.history = [
            {"role": "system", "content": SYSTEM_PROMPT.format(today=today)}
        ]

    async def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        while True:
            response = chat(
                model=settings.ollama_model,
                messages=self.history,
                tools=TOOLS,
                think=True,
            )
            msg = response.message
            self.history.append(msg)

            if not msg.tool_calls:
                return msg.content or "(модель не дала ответ)"

            for tc in msg.tool_calls:
                name = tc.function.name
                args = tc.function.arguments or {}
                print(f"  [tool] {name}({args})")
                result = await self._execute(name, args)
                self.history.append({
                    "role": "tool",
                    "tool_name": name,
                    "content": json.dumps(result, ensure_ascii=False),
                })

    async def _execute(self, name: str, args: dict):
        for t in TOOLS:
            if t.__name__ == name:
                try:
                    return await t(**args)
                except Exception as e:
                    return {"error": f"{type(e).__name__}: {e}"}
        return {"error": f"Инструмент '{name}' не найден"}
