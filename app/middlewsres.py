"""
ShablonYuStack — Telegram Business Bot Template
Author: YuraWoin (github.com/YuraWoin)
Original repository: github.com/YuraWoin/telegram_bot
Created: 2026

This code is provided for viewing and personal use only.
Do not redistribute or claim authorship. See LICENSE for terms.
"""
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable

class TestMiddleware(BaseMiddleware):
    async def __call__(self,
                        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                        event: TelegramObject,
                        data: Dict[str, Any]) -> Any:
        print('Дія до обробника')
        result = await handler(event, data)
        print('Дія після обробника')
        return result
