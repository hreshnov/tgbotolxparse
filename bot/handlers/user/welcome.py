from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
import asyncio

# [IMPORT KEYBOARDS]
from bot.keyboards.inline import main_inline
from bot.keyboards.reply import main_reply

# [IMPORT DATABASE REQUESTS]
from bot.database.requests import set_user

# [IMPORT PHRASES]
from config.loader import load_menu

from bot.handlers.user.callbacks import callbacks_previous_messages

router = Router()


phrases = load_menu()

welcome_previous_messages = {}


@router.message(CommandStart())
async def start(message: Message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    set_user(user_id)

    welcome_message = phrases['welcome_message']
    await message.answer(f'{welcome_message}, <b>{user_name}</b>', reply_markup=main_reply)
    await asyncio.sleep(0.3)

    search_instructions = phrases['search_instructions']
    await message.answer(f"{search_instructions}", reply_markup=main_inline)

    welcome_previous_messages[message.chat.id] = message.message_id

my_search = phrases['my_search']


@router.message(F.text == f"{my_search}")
async def process_search(message: Message):
    phrases = load_menu()
    search_instructions = phrases['search_instructions']
    await message.answer(f"{search_instructions}", reply_markup=main_inline)

    if message.chat.id in callbacks_previous_messages:
        await message.bot.delete_message(message.chat.id, callbacks_previous_messages[message.chat.id])
        del callbacks_previous_messages[message.chat.id]