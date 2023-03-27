from telebot import TeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.handler_backends import State, StatesGroup
from config import bot_token

bot = TeleBot(bot_token)


@bot.message_handler(commands=["start"])
def start_handler(message: Message):
    bot.send_message(message.chat.id, "Это только шаблон для нашего бота")


if __name__ == "__main__":
    bot.infinity_polling()