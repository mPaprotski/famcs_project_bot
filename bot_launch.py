from telebot import TeleBot, types
from config import BOT_TOKEN, ADMINS, SELLERS
from data_func import get_inventory_summary
from clients_func import show_clients_for_seller, update_order_status, format_order
from sheets import get_sheet

bot = TeleBot(BOT_TOKEN)

def register_handlers():
    """
    Регистрирует обработчики команд и callback-запросов для Telegram-бота.
    Инициализирует все необходимые функции для обработки входящих сообщений и действий пользователя.
    """
    
    @bot.message_handler(commands=['start'])
    def start(message):
        """
        Обрабатывает команду /start.
        Проверяет, является ли пользователь администратором или продавцом, и отображает главное меню с кнопками для управления заказами.
        Если пользователь не авторизован, отправляет сообщение о скором выпуске мерча.
        """
        username = f"@{message.from_user.username}"
        if username not in SELLERS and username not in ADMINS:
            bot.send_message(message.chat.id, "Мерч скоро будет. Ждите 🥰", parse_mode="HTML")
            return
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Список всех товаров", callback_data='data'))
        markup.add(types.InlineKeyboardButton("Список клиентов", callback_data='clients'))
        markup.add(types.InlineKeyboardButton("Список оплаченных заказов", callback_data='paid_clients'))
        markup.add(types.InlineKeyboardButton("Список доставленных заказов", callback_data='delivered_clients'))
        markup.add(types.InlineKeyboardButton("Вопрос по мерчу", url='http://t.me/paprotsky'))
        bot.send_message(message.chat.id, "Что выполняем?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == 'data')
    def handle_data(call):
        """
        Обрабатывает нажатие кнопки "Список всех товаров".
        Доступно только администраторам. Выводит сводку по инвентарю (количество товаров и их стоимость) из Google Sheets.
        """
        username = f"@{call.from_user.username}"
        if username in ADMINS:
            summary = get_inventory_summary()
            bot.send_message(call.message.chat.id, summary, parse_mode="HTML")
        else:
            bot.send_message(call.message.chat.id, "Ты не администратор)))")
        
    @bot.callback_query_handler(func=lambda call: call.data == 'clients')
    def handle_clients(call):
        """
        Обрабатывает нажатие кнопки "Список клиентов".
        Для администраторов: отображает список продавцов для выбора.
        Для продавцов: показывает список их клиентов с заказами.
        Для неавторизованных пользователей: сообщает об отказе в доступе.
        """
        username = f"@{call.from_user.username}"
        if username in ADMINS:
            markup = types.InlineKeyboardMarkup()
            bot.send_message(call.message.chat.id, "Какой продавец вас интересует?")
            for seller in SELLERS:
                markup.add(types.InlineKeyboardButton(seller, callback_data=f"seller_{seller}"))
            bot.send_message(call.message.chat.id, "Выберите продавца:", reply_markup=markup)
        elif username in SELLERS:
            show_clients_for_seller(bot, call.message.chat.id, username, status_filter=None)
        else:
            bot.send_message(call.message.chat.id, "В доступе отказано")

    @bot.callback_query_handler(func=lambda call: call.data == 'paid_clients')
    def handle_paid_clients(call):
        """
        Обрабатывает нажатие кнопки "Список оплаченных заказов".
        Для администраторов: отображает список продавцов для выбора, чтобы показать их оплаченные заказы.
        Для продавцов: показывает только их клиентов с оплаченными заказами.
        Для неавторизованных пользователей: сообщает об отказе в доступе.
        """
        username = f"@{call.from_user.username}"
        if username in ADMINS:
            markup = types.InlineKeyboardMarkup()
            bot.send_message(call.message.chat.id, "Какой продавец вас интересует?")
            for seller in SELLERS:
                markup.add(types.InlineKeyboardButton(seller, callback_data=f"seller_paid_{seller}"))
            bot.send_message(call.message.chat.id, "Выберите продавца:", reply_markup=markup)
        elif username in SELLERS:
            show_clients_for_seller(bot, call.message.chat.id, username, status_filter="Оплачено")
        else:
            bot.send_message(call.message.chat.id, "В доступе отказано")

    @bot.callback_query_handler(func=lambda call: call.data == 'delivered_clients')
    def handle_delivered_clients(call):
        """
        Обрабатывает нажатие кнопки "Список доставленных заказов".
        Для администраторов: отображает список продавцов для выбора, чтобы показать их доставленные заказы.
        Для продавцов: показывает только их клиентов с доставленными заказами.
        Для неавторизованных пользователей: сообщает об отказе в доступе.
        """
        username = f"@{call.from_user.username}"
        if username in ADMINS:
            markup = types.InlineKeyboardMarkup()
            bot.send_message(call.message.chat.id, "Какой продавец вас интересует?")
            for seller in SELLERS:
                markup.add(types.InlineKeyboardButton(seller, callback_data=f"seller_delivered_{seller}"))
            bot.send_message(call.message.chat.id, "Выберите продавца:", reply_markup=markup)
        elif username in SELLERS:
            show_clients_for_seller(bot, call.message.chat.id, username, status_filter="Доставлено")
        else:
            bot.send_message(call.message.chat.id, "В доступе отказано")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("seller_"))
    def handle_seller_selection(call):
        """
        Обрабатывает выбор конкретного продавца из списка.
        В зависимости от типа callback (все клиенты, оплаченные или доставленные заказы),
        вызывает функцию show_clients_for_seller с соответствующим фильтром по статусу.
        """
        if call.data.startswith("seller_paid_"):
            seller = call.data.split("seller_paid_", 1)[1]
            show_clients_for_seller(bot, call.message.chat.id, seller, status_filter="Оплачено")
        elif call.data.startswith("seller_delivered_"):
            seller = call.data.split("seller_delivered_", 1)[1]
            show_clients_for_seller(bot, call.message.chat.id, seller, status_filter="Доставлено")
        else:
            seller = call.data.split("seller_", 1)[1]
            show_clients_for_seller(bot, call.message.chat.id, seller, status_filter=None)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("paid_") or call.data.startswith("delivered_") or call.data.startswith("reset_"))
    def handle_status_change(call):
        """
        Обрабатывает нажатие кнопок изменения статуса заказа ("Оплачено", "Доставлено", "Сбросить статус").
        Проверяет права пользователя, обновляет статус в Google Sheets, редактирует сообщение с новой информацией о заказе.
        Обрабатывает возможные ошибки, такие как неверный индекс строки или пустой заказ.
        """
        username = f"@{call.from_user.username}"
        if username not in SELLERS and username not in ADMINS:
            bot.answer_callback_query(call.id, "У вас нет прав для изменения статуса")
            return

        try:
            action, row_index = call.data.split("_", 1)
            row_index = int(row_index)
            if action == "paid":
                new_status = "Оплачено"
            elif action == "delivered":
                new_status = "Доставлено"
            else:
                new_status = ""

            if not call.message:
                bot.answer_callback_query(call.id, "Ошибка: сообщение недоступно")
                return

            update_order_status(row_index, new_status)
            
            sheet = get_sheet()
            rows = sheet.get_all_records()
            if row_index - 2 >= len(rows) or row_index < 2:
                bot.answer_callback_query(call.id, "Ошибка: строка заказа не найдена")
                return
            
            row = rows[row_index - 2]
            items, total_price = format_order(row)
            if not items:
                bot.answer_callback_query(call.id, "Ошибка: заказ пустой")
                return

            text = (
                f"👤 <b>ФИО:</b> {row['ФИО']}\n"
                f"📞 <u>Телеграм:</u> {row['ТГ (@example)']}\n"
                f"📱 <u>Телефон:</u> {row['Номер телефона']}\n"
                f"🛍 <u><b>Заказ:</b></u>\n"
                f"<pre>{'\n'.join(items)}</pre>\n"
                f"💰<u><i>Сумма заказа:</i></u> {total_price} руб.\n"
                f"<b>Статус:</b> {new_status or 'Не указан'}"
            )
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("✅ Оплачено", callback_data=f"paid_{row_index}"))
            markup.add(types.InlineKeyboardButton("📦 Доставлено", callback_data=f"delivered_{row_index}"))
            markup.add(types.InlineKeyboardButton("🔄 Сбросить статус", callback_data=f"reset_{row_index}"))
            
            bot.edit_message_text(
                text=text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )
            status_message = "Статус сброшен" if action == "reset" else f"Статус изменен на: {new_status}"
            bot.answer_callback_query(call.id, status_message)
        except ValueError as ve:
            bot.answer_callback_query(call.id, f"Ошибка в данных: {str(ve)}")
        except Exception as e:
            bot.answer_callback_query(call.id, f"Ошибка: {str(e)}")

register_handlers()