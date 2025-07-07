import telebot
from telebot import *

bot = telebot.TeleBot("7758068587:AAHYH6xvrZy2TwtFJZ5GZ7q12CcKc3DN_lw")

@bot.message_handler(commands=['start'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Список всех товаров", callback_data='data')
    markup.row(btn1)
    btn2 = types.InlineKeyboardButton("Список клиентов", callback_data='clients')
    markup.row(btn2)
    btn3 = types.InlineKeyboardButton("Вопрос по мерчу", url='http://t.me/paprotsky')
    markup.row(btn3)
    bot.send_message(message.chat.id, "Что выполняем?", reply_markup=markup)

bot.polling(none_stop=True)
