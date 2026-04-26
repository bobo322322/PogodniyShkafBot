from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from database import is_banned

class BanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable,
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user = event.from_user
        if user.username and is_banned(user.username):
            await event.answer("⛔ Вы забанены.", show_alert=True)
            return  # не пропускаем дальше
        return await handler(event, data)