from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config.loader import load_menu


phrases = load_menu()

add_search = phrases['add_search']
main_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=f'{add_search}', callback_data='add_search')
        ]
    ]
)

support_proj = phrases['support_proj']
settings = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=f'{support_proj}', callback_data='supports')
        ]
    ]
)


city_chose = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Warszawa', callback_data='city_Warszawa'),
            InlineKeyboardButton(text='Kraków', callback_data='city_Krakow'),
        ],
        [
            InlineKeyboardButton(text='Poznań', callback_data='city_Poznan'),
            InlineKeyboardButton(text='Gdańsk', callback_data='city_Gdansk'),
        ],
        [
            InlineKeyboardButton(text='Wrocław', callback_data='city_Wroclaw'),
            InlineKeyboardButton(text='Łódź', callback_data='city_Lodz'),
        ],
        [
            InlineKeyboardButton(text='Gdynia', callback_data='city_Gdynia'),
            InlineKeyboardButton(text='Katowice', callback_data='city_Katowice'),
        ]
    ]
)


cities = {
    'Warszawa': 'https://t.me/dwelling_Warsaw',
    'Krakow': 'https://t.me/dwelling_Krakow',
    'Poznan': 'https://t.me/dwelling_Poznan',
    'Gdansk': 'https://t.me/dwelling_Gdansk',
    'Lodz': 'https://t.me/dwelling_Lodz',
    'Gdynia': 'https://t.me/dwelling_Gdinia',
    'Katowice': 'https://t.me/dwelling_Katowice',
    'Wroclaw': 'https://t.me/dwelling_Wroclaw'
}


all_ads = phrases['all_ads']
city_keyboards = {}
for city, urlc in cities.items():
    city_keyboards[city.lower() + '_city'] = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f'{all_ads}', url=urlc),
            ],
        ]
    )


edit_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Приветственное сообщение', callback_data='edit_welcome_message'),
            InlineKeyboardButton(text='Выбор города', callback_data='edit_chose_city'),
        ],
        [
            InlineKeyboardButton(text='Выбранный город', callback_data='edit_selected_city'),
            InlineKeyboardButton(text='Начало поиска', callback_data='edit_search_instructions'),
        ],
        [
            InlineKeyboardButton(text='Поддержака', callback_data='edit_support'),
            InlineKeyboardButton(text='Мои поиски', callback_data='edit_my_search'),
        ],
        [
            InlineKeyboardButton(text='Поддержать нас(кнопка на клавиатуре)', callback_data='edit_support_us'),
            InlineKeyboardButton(text='Все объявления', callback_data='edit_all_ads'),
        ],
        [
            InlineKeyboardButton(text='Поддержать проект(кнопка под текстом)', callback_data='edit_support_proj'),
            InlineKeyboardButton(text='Добавить поиск', callback_data='edit_add_search'),
        ],
        [
            InlineKeyboardButton(text='Сменить агента поддержки', callback_data='edit_tech_support'),
        ]
    ]
)