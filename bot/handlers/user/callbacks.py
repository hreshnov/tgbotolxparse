from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

# [IMPORT KEYBOARDS]
from bot.keyboards.inline import city_chose, city_keyboards

# [IMPORT DATABASE REQUESTS]
from bot.database.requests import get_user

from config.loader import bot

# [IMPORT PHRASES]
from config.loader import load_menu


router = Router()

callbacks_previous_messages = {}


@router.callback_query(F.data == 'add_search', )
async def add_search(callback: CallbackQuery):
    await callback.answer()

    phrases = load_menu()
    chose_city = phrases["chose_city"]

    await callback.message.edit_text(f'🏠 {chose_city}"', reply_markup=city_chose)
    callbacks_previous_messages[callback.message.chat.id] = callback.message.message_id


@router.callback_query(lambda query: query.data.startswith('city_'))
async def choose_city(query: CallbackQuery):
    chosen_city = query.data.split('_')[1]

    phrases = load_menu()
    selected_city = phrases["selected_city"]

    if chosen_city.lower() + '_city' in city_keyboards:
        await query.answer()
        await query.message.edit_text(f'{selected_city}', reply_markup=city_keyboards[chosen_city.lower() + '_city'])
    else:
        await query.answer("Ошибка: такого города нет в системе")

    callbacks_previous_messages[query.message.chat.id] = query.message.message_id


