from telebot import types
from config import SELLERS, PRICES, ITEMS
from sheets import get_sheet
import re

def escape_markdown(text):
    """
    Экранирует специальные символы Markdown в тексте для корректного отображения в Telegram.
    Заменяет специальные символы (например, *, _, [, ]) на их экранированные версии, чтобы предотвратить ошибки форматирования.
    
    Args:
        text (str): Входной текст для экранирования.
    
    Returns:
        str: Экранированный текст, пригодный для отправки в Telegram.
    """
    escape_chars = r'\*_`\[\]()~>#+\-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

def update_order_status(row_index, status):
    """
    Обновляет статус заказа в Google Sheets.
    Записывает указанный статус в столбец W (23-й столбец) для строки с заданным индексом.
    
    Args:
        row_index (int): Индекс строки в Google Sheets (начиная с 1).
        status (str): Новый статус заказа ("Оплачено", "Доставлено" или пустая строка для сброса).
    """
    sheet = get_sheet()
    sheet.update_cell(row_index, 23, status)

def show_clients_for_seller(bot, chat_id, tg_username, status_filter=None):
    """
    Отображает список клиентов и их заказов для конкретного продавца с возможной фильтрацией по статусу.
    Для каждого клиента, назначенного продавцу, формирует сообщение с информацией о заказе (ФИО, Telegram, телефон, товары, сумма, статус).
    Поддерживает фильтрацию по статусу заказа ("Оплачено", "Доставлено" или None для всех заказов).
    
    Args:
        bot: Экземпляр TeleBot для отправки сообщений.
        chat_id (int): ID чата для отправки сообщений.
        tg_username (str): Telegram-username продавца.
        status_filter (str, optional): Фильтр по статусу заказа ("Оплачено", "Доставлено" или None).
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

        if status_filter and row.get('Статус', '') != status_filter:
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
            f"<b>Статус:</b> {row['Статус'] or 'Не указан'}"
        )

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Оплачено", callback_data=f"paid_{i+2}"))
        markup.add(types.InlineKeyboardButton("📦 Доставлено", callback_data=f"delivered_{i+2}"))
        markup.add(types.InlineKeyboardButton("🔄 Сбросить статус", callback_data=f"reset_{i+2}"))
        bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=markup)

    if not found:
        message = (
            "На вас пока не назначено заказов."
            if status_filter is None else
            f"Нет заказов со статусом '{status_filter}'."
        )
        bot.send_message(chat_id, message)

def format_order(row):
    """
    Форматирует информацию о заказе из строки таблицы Google Sheets.
    Создает список строк с описанием товаров (название, цвет, размер, количество, стоимость) и вычисляет общую сумму заказа.
    
    Args:
        row (dict): Словарь с данными строки из Google Sheets.
    
    Returns:
        tuple: Список строк с описанием товаров и общая сумма заказа.
    """
    total_price = 0
    lines = []

    def add_item(item):
        """
        Формирует строку для одного товара в заказе.
        Проверяет количество товара, получает цвет и размер (если есть), вычисляет стоимость и добавляет информацию в список.
        
        Args:
            item (dict): Словарь с информацией о товаре из конфигурации ITEMS.
        """
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
            lines.append(f"  - {label} x{count} — {item_sum} руб.")

    for item in ITEMS:
        add_item(item)

    return lines, total_price