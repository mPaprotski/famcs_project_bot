from telebot import types
from config import SELLERS
from sheets import get_sheet

def show_clients_for_seller(bot, chat_id, tg_username):
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

        found = True
        text = (
            f"👤 *{row['ФИО']}*\n"
            f"📱 Телеграм: {row['ТГ (@example)']}\n"
            f"📞 Телефон: {row['Номер телефона']}\n"
            f"🛍 Заказ:\n"
            f"  - Футболка: {row['Расцветка футболки']} {row['Размер футболки']} x{row['Количество футболок']}\n"
            f"  - Лонгслив: {row['Расцветка лонгслива']} {row['Размер лонгслива']} x{row['Количество лонгсливов']}\n"
            f"  - Худи: {row['Расцветка худи']} {row['Размер худи']} x{row['Количество худи']}\n"
            f"  - Зип-худи: {row['Расцветка зип-худи']} {row['Размер зип-худи']} x{row['Количество зип-худи']}\n"
            f"  - Шоппер белый: {row['Шоппер белый']}, чёрный: {row['Шоппер черный']}\n"
            f"  - Кружка: {row['Кружка']}, Значок: {row['Значок']}\n"
            f"  - Блокноты: белый {row['Блокнот белый']}, чёрный {row['Блокнот черный']}\n"
            f"💬 Статус: *{row['Статус']}*"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Оплачено", callback_data=f"paid_{i+2}"))
        markup.add(types.InlineKeyboardButton("📦 Доставлено", callback_data=f"delivered_{i+2}"))
        bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)

    if not found:
        bot.send_message(chat_id, "На вас пока не назначено заказов.")
