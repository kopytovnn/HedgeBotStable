import asyncio
from typing import Text
from aiogram import Dispatcher, types
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup

from app.keyboards.simple_row import make_row_keyboard, make_inline_keyboard
from app.keyboards import buttons

# from fix.Bybit.main import start as bybit_start
from fix.Bybit.main import start

from multiprocessing import Process


router = Router()

coins = ['ADA', 'LINK', 'XRP', 'XLM', 'DASH', 'NEO', 'TRX', 'EOS', 'LTC', 'DOGE', 'APT', 'ATOM']
bybit_tasks = {}


class BybitAuthData(StatesGroup):
    waiting_for_apikey = State()
    waiting_for_secretkey = State()
    waiting_for_symbol = State()
    waiting_for_deposit = State()


@router.message(Command("bybit_start"))
@router.callback_query(F.data == "bybit_start")
async def bybit_auth_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите apikey")
    await state.set_state(BybitAuthData.waiting_for_apikey.state)


@router.message(BybitAuthData.waiting_for_apikey)
async def bybit_apikey_chosen(message: types.Message, state: FSMContext):
    await state.update_data(apikey=message.text)

    await state.set_state(BybitAuthData.waiting_for_secretkey.state)
    await message.answer("Теперь введите secretkey")


@router.message(BybitAuthData.waiting_for_secretkey)
async def bybit_secretkey_chosen(message: types.Message, state: FSMContext):
    await state.update_data(secretkey=message.text)

    await state.set_state(BybitAuthData.waiting_for_symbol.state)
    await message.answer("Введите торговую пару", reply_markup=make_inline_keyboard(coins))


@router.message(BybitAuthData.waiting_for_symbol)
@router.callback_query(F.data.startswith("bybit_change_"))
async def bybit_symbol_chosen(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(symbol=callback.data.split('_')[2])

    await state.set_state(BybitAuthData.waiting_for_deposit.state)
    await callback.message.answer("Введите желаемый депозит в usdt")


@router.message(BybitAuthData.waiting_for_deposit)
async def bybit_deposiot_chosen(message: types.Message, state: FSMContext):
    await state.update_data(deposit=message.text.lower())

    user_data = await state.get_data()
    
    apikey, secretkey, symbol, deposit = user_data.values()
    print(f'\t{symbol}\n')
    print(str(apikey), str(secretkey), symbol.upper() + 'USDT', float(deposit))
    # task = asyncio.create_task(bybit_start(str(apikey), str(secretkey), symbol.upper() + 'USDT', float(deposit)))
    # task = asyncio.to_thread(bybit_start, bybit_start(str(apikey), str(secretkey), symbol.upper() + 'USDT', float(deposit)))
    p = Process(target=start, args=(str(apikey), str(secretkey), symbol.upper() + 'USDT', float(deposit)))
    p.daemon = True
    # args=(str(apikey), str(secretkey), symbol.upper() + 'USDT', float(deposit))
    p.start()
    bybit_tasks[message.chat.id] = p
    # start(str(apikey), str(secretkey), symbol.upper() + 'USDT', float(deposit))

    await message.reply("BybBit запущен", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[buttons.BYBIT_STOP]]))    


@router.callback_query(F.data == "bybit_stop")
async def bybit_stop(callback: types.CallbackQuery):
    print(bybit_tasks)
    print(callback)
    print(bybit_tasks[callback.message.chat.id])
    # bybit_tasks[callback.message.chat.id].join()
    # bybit_tasks[callback.message.chat.id].close()
    bybit_tasks[callback.message.chat.id].kill()
    # bybit_tasks[callback.message.chat.id].join()

    await callback.message.answer("ByBit останвлен")


def register_handlers_bybit_auth(dp: Dispatcher):
    dp.register_message_handler(bybit_auth_start, commands="/bybit_auth", state="*")
    dp.register_message_handler(bybit_apikey_chosen, state=BybitAuthData.waiting_for_apikey)
    dp.register_message_handler(bybit_secretkey_chosen, state=BybitAuthData.waiting_for_secretkey)
    dp.register_message_handler(bybit_symbol_chosen, state=BybitAuthData.waiting_for_symbol)
    dp.register_message_handler(bybit_deposiot_chosen, state=BybitAuthData.waiting_for_deposit)

