
from telebot import TeleBot, types
from config import BOT_TOKEN, ADMINS, SELLERS
from data_func import get_inventory_summary
from clients_func import show_clients_for_seller, update_order_status, format_order
from sheets import get_sheet

bot = TeleBot(BOT_TOKEN)

def register_handlers():
    """
    Registers command and callback handlers for the Telegram bot.
    Initializes all required functions for processing incoming messages and user actions.
    """

    @bot.message_handler(commands=['start'])
    def start(message):
        """
        Handles the /start command.
        Checks whether the user is an admin or a seller and shows the main menu.
        If the user is not authorized, shows a merch coming soon message.
        """
        username = f"@{message.from_user.username}"
        if username not in SELLERS and username not in ADMINS:
            bot.send_message(message.chat.id, "Merch is coming soon. Stay tuned 🥰", parse_mode="HTML")
            return

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("All Product Inventory", callback_data='data'))
        markup.add(types.InlineKeyboardButton("Clients List", callback_data='clients'))
        markup.add(types.InlineKeyboardButton("Paid Orders", callback_data='paid_clients'))
        markup.add(types.InlineKeyboardButton("Delivered Orders", callback_data='delivered_clients'))
        markup.add(types.InlineKeyboardButton("Merch Question", url='http://t.me/paprotsky'))
        bot.send_message(message.chat.id, "What would you like to do?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == 'data')
    def handle_data(call):
        """
        Handles the "All Product Inventory" button.
        Available only for admins. Shows inventory summary from Google Sheets.
        """
        username = f"@{call.from_user.username}"
        if username in ADMINS:
            summary = get_inventory_summary()
            bot.send_message(call.message.chat.id, summary, parse_mode="HTML")
        else:
            bot.send_message(call.message.chat.id, "You're not an admin.")

    @bot.callback_query_handler(func=lambda call: call.data == 'clients')
    def handle_clients(call):
        """
        Handles the "Clients List" button.
        Admins can choose a seller.
        Sellers see their assigned clients.
        """
        username = f"@{call.from_user.username}"
        if username in ADMINS:
            markup = types.InlineKeyboardMarkup()
            bot.send_message(call.message.chat.id, "Which seller are you interested in?")
            for seller in SELLERS:
                markup.add(types.InlineKeyboardButton(seller, callback_data=f"seller_{seller}"))
            bot.send_message(call.message.chat.id, "Choose a seller:", reply_markup=markup)
        elif username in SELLERS:
            show_clients_for_seller(bot, call.message.chat.id, username, status_filter=None)
        else:
            bot.send_message(call.message.chat.id, "Access denied.")

    @bot.callback_query_handler(func=lambda call: call.data == 'paid_clients')
    def handle_paid_clients(call):
        """
        Handles the "Paid Orders" button.
        """
        username = f"@{call.from_user.username}"
        if username in ADMINS:
            markup = types.InlineKeyboardMarkup()
            bot.send_message(call.message.chat.id, "Which seller are you interested in?")
            for seller in SELLERS:
                markup.add(types.InlineKeyboardButton(seller, callback_data=f"seller_paid_{seller}"))
            bot.send_message(call.message.chat.id, "Choose a seller:", reply_markup=markup)
        elif username in SELLERS:
            show_clients_for_seller(bot, call.message.chat.id, username, status_filter="Paid")
        else:
            bot.send_message(call.message.chat.id, "Access denied.")

    @bot.callback_query_handler(func=lambda call: call.data == 'delivered_clients')
    def handle_delivered_clients(call):
        """
        Handles the "Delivered Orders" button.
        """
        username = f"@{call.from_user.username}"
        if username in ADMINS:
            markup = types.InlineKeyboardMarkup()
            bot.send_message(call.message.chat.id, "Which seller are you interested in?")
            for seller in SELLERS:
                markup.add(types.InlineKeyboardButton(seller, callback_data=f"seller_delivered_{seller}"))
            bot.send_message(call.message.chat.id, "Choose a seller:", reply_markup=markup)
        elif username in SELLERS:
            show_clients_for_seller(bot, call.message.chat.id, username, status_filter="Delivered")
        else:
            bot.send_message(call.message.chat.id, "Access denied.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("seller_"))
    def handle_seller_selection(call):
        if call.data.startswith("seller_paid_"):
            seller = call.data.split("seller_paid_", 1)[1]
            show_clients_for_seller(bot, call.message.chat.id, seller, status_filter="Paid")
        elif call.data.startswith("seller_delivered_"):
            seller = call.data.split("seller_delivered_", 1)[1]
            show_clients_for_seller(bot, call.message.chat.id, seller, status_filter="Delivered")
        else:
            seller = call.data.split("seller_", 1)[1]
            show_clients_for_seller(bot, call.message.chat.id, seller, status_filter=None)

    @bot.callback_query_handler(func=lambda call: call.data.startswith(("paid_", "delivered_", "reset_")))
    def handle_status_change(call):
        username = f"@{call.from_user.username}"
        if username not in SELLERS and username not in ADMINS:
            bot.answer_callback_query(call.id, "You don't have permission to change the status")
            return

        try:
            action, row_index = call.data.split("_", 1)
            row_index = int(row_index)

            if action == "paid":
                new_status = "Paid"
            elif action == "delivered":
                new_status = "Delivered"
            else:
                new_status = ""

            update_order_status(row_index, new_status)

            sheet = get_sheet()
            rows = sheet.get_all_records()
            row = rows[row_index - 2]

            items, total_price = format_order(row)
            text = (
                f"👤 <b>Name:</b> {row['ФИО']}\n"
                f"📞 <u>Telegram:</u> {row['ТГ (@example)']}\n"
                f"📱 <u>Phone:</u> {row['Номер телефона']}\n"
                f"🛍 <u><b>Order:</b></u>\n"
                f"<pre>{'\n'.join(items)}</pre>\n"
                f"💰<u><i>Order total:</i></u> {total_price} RUB\n"
                f"<b>Status:</b> {new_status or 'Not set'}"
            )

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("✅ Paid", callback_data=f"paid_{row_index}"))
            markup.add(types.InlineKeyboardButton("📦 Delivered", callback_data=f"delivered_{row_index}"))
            markup.add(types.InlineKeyboardButton("🔄 Reset status", callback_data=f"reset_{row_index}"))

            bot.edit_message_text(
                text=text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )

            bot.answer_callback_query(call.id, "Status updated successfully")
        except Exception as e:
            bot.answer_callback_query(call.id, f"Error: {str(e)}")

register_handlers()

