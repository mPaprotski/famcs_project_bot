import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
ADMINS = ['@paprotsky', '@g101t22', "@Lvmzrb"]
SELLERS = ['@mi_halk']

PRICES = {
    'футболка': 60,
    'лонгслив': 70,
    'худи': 120,
    'зип-худи': 130,
    'шоппер белый': 20,
    'шоппер черный': 20,
    'кружка': 11,
    'значок': 3,
    'блокнот белый': 6,
    'блокнот черный': 6,
}

ITEMS = [
    {
        'name': 'Футболка',
        'price_key': 'футболка',
        'color_key': 'Расцветка футболки',
        'size_key': 'Размер футболки',
        'count_key': 'Количество футболка'
    },
    {
        'name': 'Лонгслив',
        'price_key': 'лонгслив',
        'color_key': 'Расцветка лонгслива',
        'size_key': 'Размер лонгслива',
        'count_key': 'Количество лонгслив'
    },
    {
        'name': 'Худи',
        'price_key': 'худи',
        'color_key': 'Расцветка худи',
        'size_key': 'Размер худи',
        'count_key': 'Количество худи'
    },
    {
        'name': 'Зип-худи',
        'price_key': 'зип-худи',
        'color_key': 'Расцветка зип-худи',
        'size_key': 'Размер зип-худи',
        'count_key': 'Количество зип-худи'
    },
    {
        'name': 'Шоппер белый',
        'price_key': 'шоппер белый',
        'color_key': None,
        'size_key': None,
        'count_key': 'Шоппер белый'
    },
    {
        'name': 'Шоппер черный',
        'price_key': 'шоппер черный',
        'color_key': None,
        'size_key': None,
        'count_key': 'Шоппер черный'
    },
    {
        'name': 'Кружка',
        'price_key': 'кружка',
        'color_key': None,
        'size_key': None,
        'count_key': 'Кружка'
    },
    {
        'name': 'Значок',
        'price_key': 'значок',
        'color_key': None,
        'size_key': None,
        'count_key': 'Значок'
    },
    {
        'name': 'Блокнот белый',
        'price_key': 'блокнот белый',
        'color_key': None,
        'size_key': None,
        'count_key': 'Блокнот белый'
    },
    {
        'name': 'Блокнот черный',
        'price_key': 'блокнот черный',
        'color_key': None,
        'size_key': None,
        'count_key': 'Блокнот черный'
    },
]