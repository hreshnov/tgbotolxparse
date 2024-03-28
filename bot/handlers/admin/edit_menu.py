from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.inline import edit_keyboard

from bot.database.requests import add_admin, del_admin
from bot.database.models import User, LocalSession

from config.loader import load_menu

import json

admin = Router()


class EditMenuState(StatesGroup):
    waiting_for_edit = State()


class AdminProtect(Filter):
    async def __call__(self, message: Message):
        try:
            user_id = message.from_user.id
            with LocalSession() as session:
                user = session.query(User).filter_by(id=user_id, is_admin=True).first()
                return user is not None
        except Exception as e:
            print(f"Произошла ошибка при проверке администратора: {e}")
            return False


def save_phrases(phrases):
    with open('storage/phrases/phrases.json', 'w', encoding='utf-8') as file:
        json.dump(phrases, file, ensure_ascii=False, indent=4)
        print("Сохраненные фразы:", phrases)


@admin.message(AdminProtect(), Command('edit'))
async def edit(message: Message):
    await message.answer("Какой текст вы хотите редактировать?", reply_markup=edit_keyboard)


@admin.callback_query(lambda c: c.data.startswith('edit_'))
async def process_callback_button1(callback_query: CallbackQuery, state: FSMContext):
    command = callback_query.data
    phrases = load_menu()
    if command == 'edit_welcome_message':
        await state.set_state(EditMenuState.waiting_for_edit)
        await state.update_data(editing_field="welcome_message")
    elif command == 'edit_chose_city':
        await state.set_state(EditMenuState.waiting_for_edit)
        await state.update_data(editing_field="chose_city")
    elif command == 'edit_selected_city':
        await state.set_state(EditMenuState.waiting_for_edit)
        await state.update_data(editing_field="selected_city")
    elif command == 'edit_search_instructions':
        await state.set_state(EditMenuState.waiting_for_edit)
        await state.update_data(editing_field="search_instructions")
    elif command == 'edit_my_search':
        await state.set_state(EditMenuState.waiting_for_edit)
        await state.update_data(editing_field="my_search")
    elif command == 'edit_all_ads':
        await state.set_state(EditMenuState.waiting_for_edit)
        await state.update_data(editing_field="all_ads")
    elif command == 'edit_add_search':
        await state.set_state(EditMenuState.waiting_for_edit)
        await state.update_data(editing_field="add_search")
    elif command == 'edit_tech_support':
        await state.set_state(EditMenuState.waiting_for_edit)
        await state.update_data(editing_field="tech_support")

    data = await state.get_data()
    editing_field = data.get('editing_field',
                             "Поле не найдено")
    current_text = phrases.get(editing_field, "Текст не найден")
    await callback_query.message.answer(f"Текущий текст: {current_text}")
    await callback_query.message.answer(f"Введите новый текст для {command[5:]}")


@admin.message(EditMenuState.waiting_for_edit)
async def process_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    editing_field = data.get('editing_field')
    if editing_field is None:
        await message.answer("Произошла ошибка при получении поля редактирования.")
        return

    phrases = load_menu()
    phrases[editing_field] = message.text
    try:
        save_phrases(phrases)
        await message.answer("Фраза успешно обновлена.")
    except Exception as e:
        print("Ошибка при сохранении фразы:", e)
        await message.answer(f"Произошла ошибка при сохранении фразы: {e}")
    finally:
        await state.clear()


@admin.message(AdminProtect(), Command('add_admin'))
async def add_admin_handler(message: Message):
    user_id = message.text.split()[-1]
    try:
        user_id = int(user_id)
    except ValueError:
        await message.answer("Неправильный формат user_id")
        return

    try:
        add_admin(user_id)
        await message.answer(f"Пользователь с ID {user_id} был добавлен в список администраторов.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при добавлении пользователя: {e}")


@admin.message(AdminProtect(), Command('del_admin'))
async def del_admin_handler(message: Message):
    user_id = message.text.split()[-1]
    try:
        user_id = int(user_id)
    except ValueError:
        await message.answer("Неправильный формат user_id")
        return

    try:
        del_admin(user_id)
        await message.answer(f"Пользователь с ID {user_id} был удален из списка администраторов.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при удалении пользователя: {e}")