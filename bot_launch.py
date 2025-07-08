from telebot import TeleBot, types
from config import BOT_TOKEN, ADMINS, SELLERS
from data_func import get_inventory_summary
from clients_func import show_clients_for_seller

bot = TeleBot(BOT_TOKEN)

def register_handlers():
    @bot.message_handler(commands=['start'])
    def start(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Список всех товаров", callback_data='data'))
        markup.add(types.InlineKeyboardButton("Список клиентов", callback_data='clients'))
        markup.add(types.InlineKeyboardButton("Вопрос по мерчу", url='http://t.me/paprotsky'))
        bot.send_message(message.chat.id, "Что выполняем?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == 'data')
    def handle_data(call):
        summary = get_inventory_summary()
        bot.send_message(call.message.chat.id, summary)

    @bot.callback_query_handler(func=lambda call: call.data == 'clients')
    def handle_clients(call):
        user_id = call.from_user.id
        username = f"@{call.from_user.username}"
        if user_id in ADMINS:
            markup = types.InlineKeyboardMarkup()
            for seller in SELLERS:
                markup.add(types.InlineKeyboardButton(seller, callback_data=f"seller_{seller}"))
            bot.send_message(call.message.chat.id, "Выберите продавца:", reply_markup=markup)
        else:
            show_clients_for_seller(bot, call.message.chat.id, username)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("seller_"))
    def handle_seller_selection(call):
        seller = call.data.split("_")[1]
        show_clients_for_seller(bot, call.message.chat.id, seller)

register_handlers()
