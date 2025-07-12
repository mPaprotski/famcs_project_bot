from telebot import TeleBot, types
from config import BOT_TOKEN, ADMINS, SELLERS
from data_func import get_inventory_summary
from clients_func import show_clients_for_seller

bot = TeleBot(BOT_TOKEN)

def register_handlers():
    """
    Регистрирует все обработчики команд и callback-ов для телеграм бота.
    Содержит функции-обработчики для команд /start и инлайн-кнопок.
    """
    
    @bot.message_handler(commands=['start'])
    def start(message):
        """
        Обработчик команды /start. Проверяет права пользователя и показывает главное меню.
        
        Args:
            message (types.Message): Объект сообщения от пользователя
            
        Действия:
            1. Проверяет, является ли пользователь продавцом или администратором
            2. Для обычных пользователей показывает сообщение о скором появлении мерча
            3. Для авторизованных пользователей показывает меню с кнопками
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
        
        Args:
            call (types.CallbackQuery): Объект callback от инлайн-кнопки
            
        Действия:
            1. Проверяет права пользователя
            2. Для администраторов показывает сводку по товарам
            3. Для остальных показывает сообщение об отказе в доступе
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
        
        Args:
            call (types.CallbackQuery): Объект callback от инлайн-кнопки
            
        Действия:
            1. Для администраторов показывает список всех продавцов для выбора
            2. Для продавцов сразу показывает их клиентов
            3. Для остальных показывает сообщение об отказе в доступе
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
        
        Args:
            call (types.CallbackQuery): Объект callback от инлайн-кнопки
            
        Действия:
            1. Извлекает имя продавца из callback_data
            2. Показывает список клиентов для выбранного продавца
        """
        seller = call.data.split("_", 1)[1]
        show_clients_for_seller(bot, call.message.chat.id, seller)

register_handlers()