from telebot import types
from config import SELLERS, PRICES
from sheets import get_sheet
import re

def escape_markdown(text):
    """
    Экранирует специальные символы Markdown в тексте для корректного отображения в Telegram.
    """
    escape_chars = r'\*_`\[\]()~>#+\-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

def update_order_status(row_index, status):
    """
    Обновляет статус заказа в Google Sheets.
    """
    sheet = get_sheet()
    sheet.update_cell(row_index, 23, status)  # Столбец W (23-й столбец) для статуса

def show_clients_for_seller(bot, chat_id, tg_username):
    """
    Отображает список клиентов и их заказов для конкретного продавца.
    """
    sheet = get_sheet()
    rows = sheet.get_all_records()

    if tg_username not in SELLERS:
        bot.send_message(chat_id, "Вы не зарегистрированы как продавец.")
        return

    seller_index = SELLERS.index(tg_username)
    found = False

    for i, row in enumerate(rows):
        if i % len(SELLERS) != seller_index:
            continue

        items, total_price = format_order(row)
        if not items:
            continue

        found = True
        text = (
            f"👤 <b>ФИО:</b> {row['ФИО']}\n"
            f"📞 <u>Телеграм:</u> {row['ТГ (@example)']}\n"
            f"📱 <u>Телефон:</u> {row['Номер телефона']}\n"
            f"🛍 <u><b>Заказ:</b></u>\n"
            f"<pre>{'\n'.join(items)}</pre>\n"
            f"💰<u><i>Сумма заказа:</i></u> {total_price} руб.\n"
            f"<b>Статус:</b> {row['Статус']}"
        )

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Оплачено", callback_data=f"paid_{i+2}"))
        markup.add(types.InlineKeyboardButton("📦 Доставлено", callback_data=f"delivered_{i+2}"))
        bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=markup)

    if not found:
        bot.send_message(chat_id, "На вас пока не назначено заказов.")

def format_order(row):
    """
    Форматирует информацию о заказе из строки таблицы.
    """
    total_price = 0
    lines = []

    def add_item(title, color_key, size_key, count_key):
        """
        Внутренняя функция для добавления товара в список заказа.
        """
        count = row.get(count_key)
        if count and str(count).isdigit() and int(count) > 0:
            count = int(count)
            color = row.get(color_key, '').strip() if color_key else ''
            size = row.get(size_key, '').strip() if size_key else ''
            price = PRICES.get(title, 0)
            item_sum = count * price
            nonlocal total_price
            total_price += item_sum
            parts = [title]
            if color: parts.append(color)
            if size: parts.append(size)
            label = ', '.join(parts)
            lines.append(f"  - {label} x{count} — {item_sum} руб.")

    add_item('Футболка', 'Расцветка футболки', 'Размер футболки', 'Количество футболка')
    add_item('Лонгслив', 'Расцветка лонгслива', 'Размер лонгслива', 'Количество лонгслив')
    add_item('Худи', 'Расцветка худи', 'Размер худи', 'Количество худи')
    add_item('Зип-худи', 'Расцветка зип-худи', 'Размер зип-худи', 'Количество зип-худи')
    add_item('Шоппер белый', None, None, 'Шоппер белый')
    add_item('Шоппер черный', None, None, 'Шоппер черный')
    add_item('Кружка', None, None, 'Кружка')
    add_item('Значок', None, None, 'Значок')
    add_item('Блокнот белый', None, None, 'Блокнот белый')
    add_item('Блокнот черный', None, None, 'Блокнот черный')

    return lines, total_price