import asyncio
import aiohttp

from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# [IMPORT PARSE LIB]
import re
from bs4 import BeautifulSoup as bs

from fake_useragent import UserAgent

import traceback

# [IMPORT DATABASE REQUESTS]
from .database.requests import set_ad, get_all_ads

from bot.conver_currency import convert_currency


from config.loader import bot, load_menu

phrases = load_menu()


router = Router()

HEADERSOTD = {
    'user-agent': UserAgent().random,
}

BASE_URLOTD = 'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/cala-polska'


async def otodom_parse(base_urlotd):
    async with aiohttp.ClientSession(headers=HEADERSOTD) as session:
        while True:
            try:
                async with session.get(base_urlotd) as response:
                    html = await response.text()
                    soup = bs(html, 'html.parser')
                    ads = soup.find_all('a', href=re.compile(r'^/pl/oferta/'))[:100]

                    for ad in ads:
                        ad_url = ad['href']
                        if not ad_url.startswith('https://www.otodom.pl'):
                            ad_url = 'https://www.otodom.pl' + ad_url
                        async with session.get(ad_url) as ad_response:
                            ad_html = await ad_response.text()
                            ad_soup = bs(ad_html, 'html.parser')

                            title = ad_soup.find({'h1': {'class': 'css-1wnihf5 efcnut38', 'data-cy': 'adPageAdTitle'}})
                            title = title.text.strip() if title else 'No title found'

                            square = ad_soup.find('div', {'class': 'css-1wi2w6s enb64yk5',
                                                          'data-testid': 'table-value-area'})
                            square = square.text.strip() if square else 'No square found'

                            price_text = ad_soup.find('strong', {'class': 'css-t3wmkv e1l1avn10',
                                                                 'data-cy': 'adPageHeaderPrice'}).text
                            price = price_text.replace('zł', '').strip() if price_text else 'No price found'

                            room_element = ad_soup.find('a', {'class': 'css-19yhkv9 enb64yk0',
                                                              'data-cy': 'ad-information-link'})
                            room = room_element.text.strip() if room_element else 'No room info found'

                            if room == 'No room info found':
                                room_element = ad_soup.find('div', {'class': 'css-1wi2w6s enb64yk5',
                                                                    'data-testid': 'table-value-rooms_num'})
                                room = room_element.text.strip() if room_element else 'No room info found'

                            locations = ad_soup.find_all('a', {'class': 'css-1in5nid e19r3rnf1'})
                            if locations:
                                location = locations[-2].text
                            else:
                                location = ''

                            priv_element = ad_soup.find('div', {'class': 'css-1wi2w6s enb64yk5',
                                                                'data-testid': 'table-value-advertiser_type'})
                            if priv_element:
                                tenant_span = priv_element.text.strip() if priv_element else 'No tenant info found'
                                priv_mapping = {'biuro nieruchomości': 'Агенство', 'prywatny': 'Частное лицо'}
                                tenant_span = priv_mapping.get(tenant_span, 'Unknown')

                            cities = ad_soup.find_all('a', {'class': 'css-1in5nid e19r3rnf1'})
                            if cities:
                                city = cities[-3].text
                                if city in ['Gdańsk', 'Warszawa', 'Kraków', 'Wrocław', 'Katowice', 'Poznań', 'Łódź',
                                            'Gdynia']:
                                    city = cities[-3].text
                                else:
                                    city = cities[-2].text

                            else:
                                city = 'GG'


                            images = ad_soup.find_all("img")

                            image_urls = []

                            if tenant_span == 'Частное лицо':

                                for index, image in enumerate(images, start=1):
                                    if index == 2:
                                        image_url = image.get("src")
                                        if image_url:
                                            image_urls.append(image_url)

                            elif tenant_span == 'Агенство':
                                for index, image in enumerate(images, start=1):
                                    if index == 3:
                                        image_url = image.get("src")
                                        if image_url:
                                            image_urls.append(image_url)

                            images = image_urls if image_urls else ['No images found']

                            images = images

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
        message_ads_in_channel = f"[{title}]({url})\n\n#otodom\n\n📍Район: #{area}\n\n💰 Цена: {price} zł(~{int(price_usd)}$)\n🔢 Комнаты: #{room}комнаты\n〽️Площадь: {square}\n📜{tenant_span}"

        tech_support = phrases['tech_support']
        card = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Помощь в аренде', url=f'{tech_support}'),
                InlineKeyboardButton(text='К объявлению', url=url)
            ]
        ])

        await bot.send_photo(chat_id=chat_id, photo=images[0], caption=message_ads_in_channel, parse_mode='Markdown', reply_markup=card)

    except Exception as e:
        print(f"Произошла ошибка: {e}")


async def get_channel_id_by_city(city):

    channel_ids = {
        'Warszawa': '-1002129934630',
        'Kraków': '-1002010504081',
        'Wrocław': '-1002081620045',
        'Gdańsk': '-1002066491265',
        'Katowice': '-1002075629989',
        'Poznań': '-1001938453279',
        'Łódź': '-1002112567797',
        'Gdynia': '-1002118523422'
    }
    return channel_ids.get(city)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(otodom_parse(BASE_URLOTD, HEADERSOTD))