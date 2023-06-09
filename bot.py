from telebot import TeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.handler_backends import State, StatesGroup
from telebot.custom_filters import StateFilter
from telebot.storage import StateRedisStorage, StatePickleStorage
import config
import os

bot = TeleBot(config.bot_token, state_storage=StateRedisStorage(host=config.redis_host, port=config.redis_port,
                                                                password=config.redis_password))
bot.add_custom_filter(StateFilter(bot))


class MyStates(StatesGroup):
    none_state = State()
    menu_state = State()
    pack_create = State()
    pack_edit = State()
    pack_download = State()
    pack_delete = State()


@bot.message_handler(commands=["start"])
def start_handler(message: Message):
    bot.send_message(message.chat.id, "Это только шаблон для нашего бота")
    # if bot.get_state(message.from_user.id, message.chat.id) is None:
    bot.set_state(message.from_user.id, MyStates.menu_state, message.chat.id)
    if not os.path.exists("packs"):
        os.mkdir("packs")
    if not os.path.exists(f"packs/{message.chat.id}"):
        os.mkdir(f"packs/{message.chat.id}")


@bot.message_handler(state=MyStates.menu_state)
def menu_handler(message: Message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="Создать новый пак",
            callback_data="pack_create"
        )
    )
    markup.add(
        InlineKeyboardButton(
            text="Редактирование паков",
            callback_data="pack_edit"
        )
    )
    markup.add(
        InlineKeyboardButton(
            text="Выгрузка паков",
            callback_data="pack_download"
        )
    )
    markup.add(
        InlineKeyboardButton(
            text="Удаление паков",
            callback_data="pack_delete"
        )
    )
    markup.add(
        InlineKeyboardButton(
            text="Смена языка",
            callback_data="language"
        )
    )
    bot.send_message(chat_id=message.chat.id,
                     text="Меню", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "language", state=MyStates.menu_state)
def language_callback_handler(call: CallbackQuery):
    pass


@bot.callback_query_handler(func=lambda call: call.data.startswith("pack_"), state=MyStates.menu_state)
def pack_callback_handler(call: CallbackQuery):
    bot.set_state(call.from_user.id, MyStates.none_state, call.message.chat.id)
    if call.data == "pack_create":
        bot.set_state(call.from_user.id, MyStates.pack_create, call.message.chat.id)
    elif call.data == "pack_edit":
        bot.set_state(call.from_user.id, MyStates.pack_edit, call.message.chat.id)
    elif call.data == "pack_download":
        bot.set_state(call.from_user.id, MyStates.pack_download, call.message.chat.id)
    elif call.data == "pack_delete":
        bot.set_state(call.from_user.id, MyStates.pack_delete, call.message.chat.id)


@bot.message_handler(state=MyStates.pack_create)
def pack_create_handler(message: Message):
    pass


@bot.message_handler(state=MyStates.pack_delete)
def pack_delete_handler(message: Message):
    pass


@bot.message_handler(state=MyStates.pack_download)
def pack_download_handler(message: Message):
    pass


@bot.message_handler(state=MyStates.pack_edit)
def pack_edit_handler(message: Message):
    pass


if __name__ == "__main__":
    bot.infinity_polling()
