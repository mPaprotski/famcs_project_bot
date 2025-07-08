import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
ADMINS = ['@paprotsky']
SELLERS = ['@mi_halk', '@g101t22' , '@userpups']

PRICES = {
    'Футболка': 60,
    'Лонгслив': 70,
    'Худи': 120,
    'Зип-худи': 130,
    'Шоппер белый': 20,
    'Шоппер черный': 20,
    'Кружка': 11,
    'Значок': 3,
    'Блокнот белый': 6,
    'Блокнот черный': 6,
}
