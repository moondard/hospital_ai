import asyncio

from app.agent.agent import Agent


async def main():
    agent = Agent()
    print("Ассистент регистратуры. Введите 'выход' для завершения.\n")
    while True:
        try:
            user_input = input("Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nДо встречи!")
            break
        if user_input.lower() in {"выход", "exit", "quit"}:
            print("До встречи!")
            break
        if not user_input:
            continue
        try:
            reply = await agent.chat(user_input)
        except Exception as e:
            print(f"[ошибка] {type(e).__name__}: {e}")
            continue
        print(f"Ассистент: {reply}\n")


if __name__ == "__main__":
    asyncio.run(main())
