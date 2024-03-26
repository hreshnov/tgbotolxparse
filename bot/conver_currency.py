import requests


def convert_currency(amount, from_currency, to_currency):
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    response = requests.get(url)

    if response.status_code != 200:
        print("Ошибка при получении курса обмена")
        return None

    data = response.json()
    if to_currency in data['rates']:
        exchange_rate = data['rates'][to_currency]
        converted_amount = amount * exchange_rate
        return converted_amount
    else:
        print("Валюта для конвертации не найдена")
        return None


# Пример использования:
amount_in_zloty = 100
converted_amount = convert_currency(amount_in_zloty, 'PLN', 'USD')
if converted_amount is not None:
    print(f"{amount_in_zloty} PLN = {converted_amount:.2f} USD")
