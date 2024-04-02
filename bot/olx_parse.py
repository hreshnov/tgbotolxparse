import asyncio
import aiohttp

from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# [IMPORT PARSE LIB]
import re
from bs4 import BeautifulSoup as bs

from fake_useragent import UserAgent

import traceback

from bot.conver_currency import convert_currency

# [IMPORT DATABASE REQUESTS]
from .database.requests import set_ad, get_all_ads


from config.loader import bot, load_menu

phrases = load_menu()


router = Router()

HEADERS = {
    'user-agent': UserAgent().random,
}

BASE_URL = 'https://www.olx.pl/nieruchomosci/mieszkania/wynajem/'


async def olx_parse(base_url, HEADERS):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        while True:
            try:
                async with session.get(base_url) as response:
                    html = await response.text()
                    soup = bs(html, 'html.parser')
                    ads = soup.find_all('a', {'class': 'css-rc5s2u'})[:100]

                    for ad in ads:
                        ad_url = ad['href']
                        if not ad_url.startswith('https://www.olx.pl'):
                            ad_url = 'https://www.olx.pl/' + ad_url
                        async with session.get(ad_url) as ad_response:
                            ad_html = await ad_response.text()
                            ad_soup = bs(ad_html, 'html.parser')

                            locations = ad_soup.find_all('a', {'class': 'css-tyi2d1'})
                            if locations:
                                location = locations[-1].text.replace('Wynajem - ', '').strip()
                            else:
                                location = ''

                            title_da = ad_soup.find({'div': {'class': 'css-1yzzyg0', 'data-cy': 'ad_title'}})
                            title = title_da.find('h4', {'class': 'css-1juynto'})
                            title = title.text.strip() if title else 'No title found'

                            images = [img['src'] for img in ad_soup.find_all('img', class_='css-1bmvjcs')]

                            cities = ad_soup.find_all('a', {'class': 'css-tyi2d1'})
                            if cities:
                                city = cities[-2].text
                            else:
                                city = ''

                            price_da = ad_soup.find('div', {'class': 'css-e2ir3r'})
                            price_text = price_da.find('h3').text.strip() if price_da else 'No price found'
                            price = price_text.replace('zł', '').strip() if price_text else 'No price found'

                            room = ad_soup.find('p', {'class': 'css-b5m1rv er34gjf0'}, string=re.compile(r'Liczba pokoi:', re.IGNORECASE))
                            room_text = room.text.strip() if room else 'No room info found'
                            room = room_text.replace('Liczba pokoi:', '').strip().split()[0]

                            square = ad_soup.find('p', {'class': 'css-b5m1rv er34gjf0'}, string=re.compile(r'Powierzchnia:', re.IGNORECASE))
                            square_text = square.text.strip() if square else 'No square info found'
                            square = square_text.replace('Powierzchnia:', '').strip()

                            tenant_paragraph = ad_soup.find('p', {'class': 'css-b5m1rv er34gjf0'})
                            tenant_span = 'No tenant info found'
                            tenant_span_mapping = {'Firmowe': 'Агенство', 'Prywatne': 'Частное лицо'}
                            if tenant_paragraph:
                                tenant_span = tenant_paragraph.find_next('span').text.strip()
                                tenant_span = tenant_span_mapping.get(tenant_span, 'No tenant info found')

                            if not await is_ad_in_database(title):
                                await send_ad_to_channel(title, location, price, room, square, tenant_span, ad_url, images, city)
                await asyncio.sleep(20)
            except Exception:
                traceback.print_exc()


async def is_ad_in_database(title):
    all_ads = await get_all_ads()
    if not all_ads:
        return False
    return any(title == ad.title for ad in all_ads)


async def send_ad_to_channel(title, area, price, room, square, tenant_span, url, images, city):
    try:
        if await is_ad_in_database(title):
            # print("Объявление уже в базе данных")
            return

        chat_id = await get_channel_id_by_city(city)
        if not chat_id:
            # print(f"Нет канала для города {city}. Объявление не будет отправлено.")
            return

        price_cleaned = price.replace(' ', '')
        price_usd = convert_currency(float(price_cleaned), 'PLN', 'USD')
        if price_usd is None:
            print("Не удалось конвертировать цену")
            return

        set_ad(title, area, price, room, square, tenant_span, url, images, city)
        message_ads_in_channel = f"[{title}]({url})\n\n#olx\n\n📍Район: #{area}\n\n💰 Цена: {price} zł(~{int(price_usd)}$)\n🔢 Комнаты: #{room}комнаты\n〽️Площадь: {square}\n📜{tenant_span}"

        tech_support = phrases['tech_support']
        card = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Помощь в аренде', url=f'{tech_support}'),
                InlineKeyboardButton(text='К объявлению', url=url)
            ]
        ])

        await bot.send_photo(chat_id=chat_id, photo=images[0], caption=message_ads_in_channel, parse_mode='Markdown', reply_markup=card)

    except Exception:
        traceback.print_exc()


async def get_channel_id_by_city(city):

    channel_ids = {
        'Wynajem - Warszawa': '-1002129934630',
        'Wynajem - Kraków': '-1002010504081',
        'Wynajem - Wrocław': '-1002081620045',
        'Wynajem - Gdańsk': '-1002066491265',
        'Wynajem - Katowice': '-1002075629989',
        'Wynajem - Poznań': '-1001938453279',
        'Wynajem - Łódź': '-1002112567797',
        'Wynajem - Gdynia': '-1002118523422'
    }
    return channel_ids.get(city)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(olx_parse(BASE_URL, HEADERS))