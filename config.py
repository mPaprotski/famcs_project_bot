import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
ADMINS = ['@mPaprotski', '@g101t22', "@Lvmzrb"]
SELLERS = ['@mi_halk', '@aboba', '@serb']

PRICES = {
    't-shirt': 60,
    'longsleeve': 70,
    'hoodie': 120,
    'zip-hoodie': 130,
    'shopper white': 20,
    'shopper black': 20,
    'mug': 11,
    'badge': 3,
    'notebook white': 6,
    'notebook black': 6,
}

ITEMS = [
    {
        'name': 'T-shirt',
        'price_key': 't-shirt',
        'color_key': 'T-shirt color',
        'size_key': 'T-shirt size',
        'count_key': 'T-shirt quantity'
    },
    {
        'name': 'Longsleeve',
        'price_key': 'longsleeve',
        'color_key': 'Longsleeve color',
        'size_key': 'Longsleeve size',
        'count_key': 'Longsleeve quantity'
    },
    {
        'name': 'Hoodie',
        'price_key': 'hoodie',
        'color_key': 'Hoodie color',
        'size_key': 'Hoodie size',
        'count_key': 'Hoodie quantity'
    },
    {
        'name': 'Zip-hoodie',
        'price_key': 'zip-hoodie',
        'color_key': 'Zip-hoodie color',
        'size_key': 'Zip-hoodie size',
        'count_key': 'Zip-hoodie quantity'
    },
    {
        'name': 'Shopper white',
        'price_key': 'shopper white',
        'color_key': None,
        'size_key': None,
        'count_key': 'Shopper white'
    },
    {
        'name': 'Shopper black',
        'price_key': 'shopper black',
        'color_key': None,
        'size_key': None,
        'count_key': 'Shopper black'
    },
    {
        'name': 'Mug',
        'price_key': 'mug',
        'color_key': None,
        'size_key': None,
        'count_key': 'Mug'
    },
    {
        'name': 'Badge',
        'price_key': 'badge',
        'color_key': None,
        'size_key': None,
        'count_key': 'Badge'
    },
    {
        'name': 'Notebook white',
        'price_key': 'notebook white',
        'color_key': None,
        'size_key': None,
        'count_key': 'Notebook white'
    },
    {
        'name': 'Notebook black',
        'price_key': 'notebook black',
        'color_key': None,
        'size_key': None,
        'count_key': 'Notebook black'
    },
]
