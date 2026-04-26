import asyncio
from aiogram import Bot

async def main():
    bot = Bot(token="8225047168:AAHUfxCJ9l1XLSrQtI8yAGTKgPaP4hU78WQ")
    user_chat_id = 1052265014
    message_text = "👊"


    try:
        await bot.send_message(chat_id=user_chat_id, text=message_text)
        print("Сообщение отправлено!")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())