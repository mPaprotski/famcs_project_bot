from telebot import TeleBot, types
from config import BOT_TOKEN, ADMINS, SELLERS
from data_func import get_inventory_summary
from clients_func import show_clients_for_seller

bot = TeleBot(BOT_TOKEN)

def register_handlers():
    @bot.message_handler(commands=['start'])
    def start(message):
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
        username = f"@{call.from_user.username}"
        if username in ADMINS:
            summary = get_inventory_summary()
            bot.send_message(call.message.chat.id, summary, parse_mode="HTML")
        else:
            bot.send_message(call.message.chat.id, "Ты не администратор)))")
        
    @bot.callback_query_handler(func=lambda call: call.data == 'clients')
    def handle_clients(call):
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
        seller = call.data.split("_", 1)[1]
        show_clients_for_seller(bot, call.message.chat.id, seller)

register_handlers()