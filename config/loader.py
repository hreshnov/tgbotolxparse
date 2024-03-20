from aiogram import Bot, Dispatcher

from config.config import TOKEN

import json

ENGINE = 'sqlite+aiosqlite:///db.sqlite3'
ECHO = True

bot = Bot(token=TOKEN, parse_mode='HTML')
dp = Dispatcher()


def load_menu():
    with open('storage/phrases/phrases.json', 'r', encoding="utf-8") as file:
        phrases = json.load(file)
        return phrases