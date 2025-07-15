from telebot import TeleBot, types
from config import BOT_TOKEN, ADMINS, SELLERS
from data_func import get_inventory_summary
from clients_func import show_clients_for_seller, update_order_status, format_order
from sheets import get_sheet

bot = TeleBot(BOT_TOKEN)

def register_handlers():
    """
    Регистрирует все обработчики команд и callback-ов для телеграм бота.
    """
    
    @bot.message_handler(commands=['start'])
    def start(message):
        """
        Обработчик команды /start. Проверяет права пользователя и показывает главное меню.
        """
        username = f"@{message.from_user.username}"
        if username not in SELLERS and username not in ADMINS:
            bot.send_message(message.chat.id, "Мерч скоро будет. Ждите 🥰", parse_mode="HTML")
            return
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Список всех товаров", callback_data='data'))
        markup.add(types.InlineKeyboardButton("Список клиентов", callback_data='clients'))
        markup.add(types.InlineKeyboardButton("Вопрос по мерчу", url='http://t.me/paprotsky'))
        bot.send_message(message.chat.id, "Что выполняем?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == 'data')
    def handle_data(call):
        """
        Обработчик кнопки "Список всех товаров". Доступен только администраторам.
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
        Обработчик кнопки "Список клиентов". Имеет разное поведение для админов и продавцов.
        """
        username = f"@{call.from_user.username}"
        if username in ADMINS:
            markup = types.InlineKeyboardMarkup()
            bot.send_message(call.message.chat.id, "Какой продавец вас интересует?")
            for seller in SELLERS:
                markup.add(types.InlineKeyboardButton(seller, callback_data=f"seller_{seller}"))
            bot.send_message(call.message.chat.id, "Выберите продавца:", reply_markup=markup)
        elif username in SELLERS:
            show_clients_for_seller(bot, call.message.chat.id, username)
        else:
            bot.send_message(call.message.chat.id, "В доступе отказано")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("seller_"))
    def handle_seller_selection(call):
        """
        Обработчик выбора конкретного продавца из списка.
        """
        seller = call.data.split("_", 1)[1]
        show_clients_for_seller(bot, call.message.chat.id, seller)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("paid_") or call.data.startswith("delivered_") or call.data.startswith("reset_"))
    def handle_status_change(call):
        """
        Обработчик кнопок изменения статуса заказа.
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
                new_status = ""  # Сброс статуса

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