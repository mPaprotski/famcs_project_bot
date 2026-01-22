from telebot import types
from config import SELLERS, PRICES, ITEMS
from sheets import get_sheet
import re

def escape_markdown(text):
    """
    Escapes Markdown special characters in text for safe Telegram rendering.
    Replaces characters like *, _, [, ] with escaped versions to prevent formatting issues.

    Args:
        text (str): Input text to escape.

    Returns:
        str: Escaped text.
    """
    escape_chars = r'\*_`\[\]()~>#+\-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

def update_order_status(row_index, status):
    """
    Updates order status in Google Sheets.
    Writes the specified status into column W (23rd column) for the given row index.

    Args:
        row_index (int): Row index in Google Sheets (starting from 1).
        status (str): New order status ("Paid", "Delivered" or empty string for reset).
    """
    sheet = get_sheet()
    sheet.update_cell(row_index, 23, status)

def show_clients_for_seller(bot, chat_id, tg_username, status_filter=None):
    """
    Displays a list of clients and their orders for a specific seller with optional status filtering.
    For each client assigned to the seller, sends a message with order info (name, Telegram, phone, items, total, status).

    Args:
        bot: TeleBot instance for sending messages.
        chat_id (int): Chat ID to send messages to.
        tg_username (str): Telegram username of the seller.
        status_filter (str, optional): Order status filter ("Paid", "Delivered", or None).
    """
    sheet = get_sheet()
    rows = sheet.get_all_records()

    if tg_username not in SELLERS:
        bot.send_message(chat_id, "You're not registered as a seller.")
        return

    seller_index = SELLERS.index(tg_username)
    found = False

    for i, row in enumerate(rows):
        if i % len(SELLERS) != seller_index:
            continue

        if status_filter and row.get('Status', '') != status_filter:
            continue

        items, total_price = format_order(row)
        if not items:
            continue

        found = True
        text = (
            f"👤 <b>Name:</b> {row['ФИО']}\n"
            f"📞 <u>Telegram:</u> {row['ТГ (@example)']}\n"
            f"📱 <u>Phone:</u> {row['Номер телефона']}\n"
            f"🛍 <u><b>Order:</b></u>\n"
            f"<pre>{'\n'.join(items)}</pre>\n"
            f"💰<u><i>Order total:</i></u> {total_price} RUB\n"
            f"<b>Status:</b> {row['Status'] or 'Not set'}"
        )

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Paid", callback_data=f"paid_{i+2}"))
        markup.add(types.InlineKeyboardButton("📦 Delivered", callback_data=f"delivered_{i+2}"))
        markup.add(types.InlineKeyboardButton("🔄 Reset status", callback_data=f"reset_{i+2}"))
        bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=markup)

    if not found:
        message = (
            "You don't have any assigned orders yet."
            if status_filter is None else
            f"No orders with status '{status_filter}'."
        )
        bot.send_message(chat_id, message)

def format_order(row):
    """
    Formats order info from a Google Sheets row.
    Creates a list of item lines (name, color, size, quantity, cost) and calculates total price.

    Args:
        row (dict): Row data from Google Sheets.

    Returns:
        tuple: List of item descriptions and total price.
    """
    total_price = 0
    lines = []

    def add_item(item):
        count = row.get(item['count_key'])
        if count and str(count).isdigit() and int(count) > 0:
            count = int(count)
            color = row.get(item['color_key'], '').strip() if item['color_key'] else ''
            size = row.get(item['size_key'], '').strip() if item['size_key'] else ''
            price = PRICES.get(item['price_key'], 0)
            item_sum = count * price
            nonlocal total_price
            total_price += item_sum
            parts = [item['name']]
            if color: parts.append(color)
            if size: parts.append(size)
            label = ', '.join(parts)
            lines.append(f"  - {label} x{count} — {item_sum} RUB")

    for item in ITEMS:
        add_item(item)

    return lines, total_price
