from aiogram import Router, F
from aiogram.types import Message

# [IMPORT KEYBOARDS]
from bot.keyboards.inline import settings

# [IMPORT DATABASE REQUESTS]
from bot.database.requests import get_user

# [IMPORT PHRASES]
from config.loader import load_menu


router = Router()


phrases = load_menu()

