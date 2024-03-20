from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config.loader import load_menu


keyboard_buttons = []

phrases = load_menu()

my_search = phrases['my_search']
support_us = phrases['support_us']
keyboard_buttons.append([KeyboardButton(text=my_search)])
keyboard_buttons.append([KeyboardButton(text=support_us)])


main_reply = ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)