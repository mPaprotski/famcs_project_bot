import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
ADMINS = ['@paprotsky']
SELLERS = ['@mi_halk', '@g101t22' , '@d_mandarincha']

PRICES = {
    'футболок': 60,
    'лонгсливов': 70,
    'худи': 120,
    'зип-худи': 130,
    'шоппер белый': 20,
    'шоппер черный': 20,
    'кружка': 11,
    'значок': 3,
    'блокнот белый': 6,
    'блокнот черный': 6,
}
