import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import TOKEN

from app.handlers import common, bybit_handler, bingx_handler

from aiogram.filters import CommandStart

from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject

from aiogram.types import Message

import multiprocessing as mp

from fix.Bybit.main import start


# from telegram_core.app.handlers import bybit_handler

class SomeMiddleware(BaseMiddleware):
    def __init__(self, allowed_users):
        super().__init__()
        self.allowed_users = allowed_users

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # print(event.chat)
        user_id = event.chat.id
        if user_id not in self.allowed_users:
            return 0
            # raise CancelHandler()  # Остановка дальнейшей обработки
        result = await handler(event, data)
        print("After handler")
        return result



async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(TOKEN)

    allowed_users = [540862463,
                     6111704436,
                     7493850317,
                     6755106282,
                     925216062]
    common.router.message.middleware(SomeMiddleware(allowed_users))
    bybit_handler.router.message.middleware(SomeMiddleware(allowed_users))
    bingx_handler.router.message.middleware(SomeMiddleware(allowed_users))


    dp.include_router(common.router)
    dp.include_router(bybit_handler.router)
    dp.include_router(bingx_handler.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())