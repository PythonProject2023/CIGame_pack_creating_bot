from telebot import TeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.handler_backends import State, StatesGroup
from telebot.custom_filters import StateFilter
from telebot.storage import StateRedisStorage
from telebot.util import quick_markup
from uuid import uuid1
import config
import os


bot = TeleBot(config.bot_token, state_storage=StateRedisStorage())
bot.add_custom_filter(StateFilter(bot))


class MyStates(StatesGroup):
    none_state = State()
    menu_state = State()
    pack_create = State()
    pack_edit = State()
    round_create = State()
    round_final_create = State()
    round_edit = State()
    theme_create = State()
    theme_edit = State()
    question_create = State()
    question_edit = State()
    question_cost = State()
    question_answer = State()
    question_question = State()


@bot.message_handler(commands=["start"])
def start_handler(message: Message):
    print(f"{message.chat.id} in start")
    # if bot.get_state(message.from_user.id, message.chat.id) is None:
    bot.set_state(message.from_user.id, MyStates.menu_state, message.chat.id)
    # bot.send_message(message.chat.id, "Это только шаблон для нашего бота")
    if not os.path.exists("../packs"):
        os.mkdir("../packs")
    if not os.path.exists(f"../packs/{message.chat.id}"):
        os.mkdir(f"../packs/{message.chat.id}")
    menu_handler(message)


# @bot.message_handler(state=MyStates.menu_state)
def menu_handler(message: Message):
    print(f"{message.chat.id} in menu")
    markup = quick_markup({
        "Создать новый пак": {"callback_data": "pack_create"},
        "Редактировать пак": {"callback_data": "pack_edit"},
        "Выгрузить пак": {"callback_data": "pack_download"},
        "Удалить пак": {"callback_data": "pack_delete"},
        "Смена языка": {"callback_data": "language"}
    })
    try:
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id, text="Меню", reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=message.chat.id,
                         text="Меню", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "language", state=MyStates.menu_state)
def language_callback_handler(call: CallbackQuery):
    print(f"{call.message.chat.id} in lng")
    if call.message.text != "Не удалось сменить язык":
        markup = quick_markup({
            "Создать новый пак": {"callback_data": "pack_create"},
            "Редактировать пак": {"callback_data": "pack_edit"},
            "Выгрузить пак": {"callback_data": "pack_download"},
            "Удалить пак": {"callback_data": "pack_delete"},
            "Смена языка": {"callback_data": "language"}
        })
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text="Не удалось сменить язык", reply_markup=markup)
    # bot.send_message(call.message.chat.id, "Не удалось сменить язык")
    # menu_handler(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "pack_create", state=MyStates.menu_state)
def pack_create_callback_handler(call: CallbackQuery):
    print(f"{call.message.chat.id} in pack create 1")
    bot.set_state(call.from_user.id, MyStates.pack_create, call.message.chat.id)
    bot.send_message(call.message.chat.id, "Введите название пака:")


@bot.message_handler(state=MyStates.pack_create)
def pack_create_handler(message: Message):
    print(f"{message.chat.id} in pack create 2")
    bot.set_state(message.from_user.id, MyStates.menu_state, message.chat.id)
    bot.add_data(message.from_user.id, message.chat.id, pack=message.text)
    # bot.send_message(message.chat.id, "Успешно")
    menu_handler(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("pack_d"), state=MyStates.menu_state)
def pack_download_delete_callback_handler(call: CallbackQuery):
    list_of_packs = ["first", "second", "haha", "anime"]
    markup = InlineKeyboardMarkup(row_width=1)
    if call.data == "pack_delete":
        for i in list_of_packs:
            markup.add(InlineKeyboardButton(i, callback_data=f"delete_pack_{i}"))
        markup.add(InlineKeyboardButton("Назад", callback_data="back_to_menu"))
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Нажмите, чтобы удалить", reply_markup=markup)
    elif call.data == "pack_download":
        for i in list_of_packs:
            markup.add(InlineKeyboardButton(i, callback_data=f"download_pack_{i}"))
        markup.add(InlineKeyboardButton("Назад", callback_data="back_to_menu"))
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Нажмите, чтобы скачать", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "pack_edit", state=MyStates.menu_state)
def pack_edit_list_callback_handler(call: CallbackQuery):
    list_of_packs = ["first", "second", "haha", "anime"]
    markup = InlineKeyboardMarkup(row_width=1)
    for i in list_of_packs:
        markup.add(InlineKeyboardButton(i, callback_data=f"edit_pack_{i}"))
    markup.add(InlineKeyboardButton("Назад", callback_data="back_to_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Нажмите, чтобы редактировать", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("download_pack_"), state=MyStates.menu_state)
def pack_download_callback_handler(call: CallbackQuery):
    name = call.data[14:]
    print(name)
    # bot.send_message(call.message.chat.id, "Успешно")
    menu_handler(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_pack_"), state=MyStates.menu_state)
def pack_delete_callback_handler(call: CallbackQuery):
    name = call.data[12:]
    print(name)
    # bot.send_message(call.message.chat.id, "Успешно")
    menu_handler(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu", state=MyStates.menu_state)
def back_menu_callback_handler(call: CallbackQuery):
    menu_handler(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_pack_"), state=MyStates.menu_state)
def pack_edit_callback_handler(call: CallbackQuery):
    bot.set_state(call.from_user.id, MyStates.pack_edit, call.message.chat.id)
    name = call.data[10:]
    bot.add_data(call.from_user.id, call.message.chat.id, pack=name)
    print(name)
    pack_edit_handler(call)


# @bot.message_handler(state=MyStates.pack_edit)
def pack_edit_handler(call: CallbackQuery):
    markup = quick_markup({
        "Создать финальный раунд": {"callback_data": "round_final_create"},
        "Создать раунд": {"callback_data": "round_create"},
        "Редактировать раунд": {"callback_data": "round_edit"},
        "Удалить раунд": {"callback_data": "round_delete"},
        "Назад": {"callback_data": "back_to_edit_pack_list"}
    }, row_width=1)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        pack = data["pack"]
    txt = f"Меню\n\nПак {pack}"
    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=call.message.chat.id,
                         text=txt, reply_markup=markup)


def pack_edit_msg_handler(message: Message):
    markup = quick_markup({
        "Создать финальный раунд": {"callback_data": "round_final_create"},
        "Создать раунд": {"callback_data": "round_create"},
        "Редактировать раунд": {"callback_data": "round_edit"},
        "Удалить раунд": {"callback_data": "round_delete"},
        "Назад": {"callback_data": "back_to_edit_pack_list"}
    }, row_width=1)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        pack = data["pack"]
    txt = f"Меню\n\nПак {pack}"
    try:
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id,
                              text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=message.chat.id,
                         text=txt, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_edit_pack_list", state=MyStates.pack_edit)
def back_menu_callback_handler(call: CallbackQuery):
    bot.set_state(call.from_user.id, MyStates.menu_state, call.message.chat.id)
    pack_edit_list_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "round_create", state=MyStates.pack_edit)
def round_create_callback_handler(call: CallbackQuery):
    print(f"{call.message.chat.id} in round create 1")
    bot.set_state(call.from_user.id, MyStates.round_create, call.message.chat.id)
    bot.send_message(call.message.chat.id, "Введите название раунда:")


@bot.message_handler(state=MyStates.round_create)
def round_create_handler(message: Message):
    print(f"{message.chat.id} in round create 2")
    bot.set_state(message.from_user.id, MyStates.pack_edit, message.chat.id)
    bot.add_data(message.from_user.id, message.chat.id, round=message.text)
    pack_edit_msg_handler(message)


@bot.callback_query_handler(func=lambda call: call.data == "round_final_create", state=MyStates.pack_edit)
def round_final_create_callback_handler(call: CallbackQuery):
    print(f"{call.message.chat.id} in final round create 1")
    bot.set_state(call.from_user.id, MyStates.round_final_create, call.message.chat.id)
    bot.send_message(call.message.chat.id, "Введите название раунда:")


@bot.message_handler(state=MyStates.round_final_create)
def round_final_create_handler(message: Message):
    print(f"{message.chat.id} in final round create 2")
    bot.set_state(message.from_user.id, MyStates.pack_edit, message.chat.id)
    bot.add_data(message.from_user.id, message.chat.id, round=message.text)
    pack_edit_msg_handler(message)


@bot.callback_query_handler(func=lambda call: call.data == "round_delete", state=MyStates.pack_edit)
def round_delete_callback_handler(call: CallbackQuery):
    list_of_rounds = ["first", "second", "lol", "anime"]
    markup = InlineKeyboardMarkup(row_width=1)
    for i in list_of_rounds:
        markup.add(InlineKeyboardButton(i, callback_data=f"delete_round_{i}"))
    markup.add(InlineKeyboardButton("Назад", callback_data="back_to_pack_edit_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Нажмите, чтобы удалить", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "round_edit", state=MyStates.pack_edit)
def round_edit_list_callback_handler(call: CallbackQuery):
    list_of_rounds = ["first", "second", "lol", "anime"]
    markup = InlineKeyboardMarkup(row_width=1)
    for i in list_of_rounds:
        markup.add(InlineKeyboardButton(i, callback_data=f"edit_round_{i}"))
    markup.add(InlineKeyboardButton("Назад", callback_data="back_to_pack_edit_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Нажмите, чтобы редактировать", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_pack_edit_menu", state=MyStates.pack_edit)
def back_menu_callback_handler(call: CallbackQuery):
    pack_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_round_"), state=MyStates.pack_edit)
def round_delete_callback_handler(call: CallbackQuery):
    name = call.data[13:]
    print(name)
    # bot.send_message(call.message.chat.id, "Успешно")
    pack_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_round_"), state=MyStates.pack_edit)
def round_edit_callback_handler(call: CallbackQuery):
    bot.set_state(call.from_user.id, MyStates.round_edit, call.message.chat.id)
    name = call.data[11:]
    bot.add_data(call.from_user.id, call.message.chat.id, round=name)
    print(name)
    round_edit_handler(call)


# @bot.message_handler(state=MyStates.round_edit)
def round_edit_handler(call: CallbackQuery):
    markup = quick_markup({
        "Создать тему": {"callback_data": "theme_create"},
        "Редактировать тему": {"callback_data": "theme_edit"},
        "Удалить тему": {"callback_data": "theme_delete"},
        "Назад": {"callback_data": "back_to_edit_round_list"}
    }, row_width=1)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        pack_ = data["pack"]
        round_ = data["round"]
    txt = f"Меню\n\nПак {pack_}\nРаунд {round_}"
    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=call.message.chat.id,
                         text=txt, reply_markup=markup)


def round_edit_msg_handler(message: Message):
    markup = quick_markup({
        "Создать тему": {"callback_data": "theme_create"},
        "Редактировать тему": {"callback_data": "theme_edit"},
        "Удалить тему": {"callback_data": "theme_delete"},
        "Назад": {"callback_data": "back_to_edit_round_list"}
    }, row_width=1)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        pack_ = data["pack"]
        round_ = data["round"]
    txt = f"Меню\n\nПак {pack_}\nРаунд {round_}"
    try:
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id, text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=message.chat.id,
                         text=txt, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_edit_round_list", state=MyStates.round_edit)
def back_menu_round_callback_handler(call: CallbackQuery):
    bot.set_state(call.from_user.id, MyStates.pack_edit, call.message.chat.id)
    round_edit_list_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "theme_create", state=MyStates.round_edit)
def theme_create_callback_handler(call: CallbackQuery):
    print(f"{call.message.chat.id} in theme create 1")
    bot.set_state(call.from_user.id, MyStates.theme_create, call.message.chat.id)
    bot.send_message(call.message.chat.id, "Введите название темы:")


@bot.message_handler(state=MyStates.theme_create)
def theme_create_handler(message: Message):
    print(f"{message.chat.id} in theme create 2")
    bot.set_state(message.from_user.id, MyStates.round_edit, message.chat.id)
    bot.add_data(message.from_user.id, message.chat.id, theme=message.text)
    round_edit_msg_handler(message)


@bot.callback_query_handler(func=lambda call: call.data == "theme_delete", state=MyStates.round_edit)
def theme_delete_callback_handler(call: CallbackQuery):
    list_of_theme = ["first", "second", "lol", "anime"]
    markup = InlineKeyboardMarkup(row_width=1)
    for i in list_of_theme:
        markup.add(InlineKeyboardButton(i, callback_data=f"delete_theme_{i}"))
    markup.add(InlineKeyboardButton("Назад", callback_data="back_to_round_edit_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Нажмите, чтобы удалить", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "theme_edit", state=MyStates.round_edit)
def theme_edit_list_callback_handler(call: CallbackQuery):
    list_of_theme = ["first", "second", "lol", "anime"]
    markup = InlineKeyboardMarkup(row_width=1)
    for i in list_of_theme:
        markup.add(InlineKeyboardButton(i, callback_data=f"edit_theme_{i}"))
    markup.add(InlineKeyboardButton("Назад", callback_data="back_to_round_edit_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Нажмите, чтобы редактировать", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_round_edit_menu", state=MyStates.round_edit)
def back_menu_theme_callback_handler(call: CallbackQuery):
    round_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_theme_"), state=MyStates.round_edit)
def theme_delete_callback_handler(call: CallbackQuery):
    name = call.data[13:]
    print(name)
    # bot.send_message(call.message.chat.id, "Успешно")
    round_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_theme_"), state=MyStates.round_edit)
def theme_edit_callback_handler(call: CallbackQuery):
    bot.set_state(call.from_user.id, MyStates.theme_edit, call.message.chat.id)
    name = call.data[11:]
    bot.add_data(call.from_user.id, call.message.chat.id, theme=name)
    print(name)
    theme_edit_handler(call)


# @bot.message_handler(state=MyStates.theme_edit)
def theme_edit_handler(call: CallbackQuery):
    markup = quick_markup({
        "Создать вопрос": {"callback_data": "question_create"},
        "Редактировать вопрос": {"callback_data": "question_edit"},
        "Удалить вопрос": {"callback_data": "question_delete"},
        "Назад": {"callback_data": "back_to_edit_theme_list"}
    }, row_width=1)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        pack_ = data["pack"]
        round_ = data["round"]
        theme_ = data["theme"]
    txt = f"Меню\n\nПак {pack_}\nРаунд {round_}\nТема {theme_}"
    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=call.message.chat.id,
                         text=txt, reply_markup=markup)


def theme_edit_msg_handler(message: Message):
    markup = quick_markup({
        "Создать вопрос": {"callback_data": "question_create"},
        "Редактировать вопрос": {"callback_data": "question_edit"},
        "Удалить вопрос": {"callback_data": "question_delete"},
        "Назад": {"callback_data": "back_to_edit_theme_list"}
    }, row_width=1)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        pack_ = data["pack"]
        round_ = data["round"]
        theme_ = data["theme"]
    txt = f"Меню\n\nПак {pack_}\nРаунд {round_}\nТема {theme_}"
    try:
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id, text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=message.chat.id,
                         text=txt, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_edit_theme_list", state=MyStates.theme_edit)
def back_menu_theme_callback_handler(call: CallbackQuery):
    bot.set_state(call.from_user.id, MyStates.round_edit, call.message.chat.id)
    theme_edit_list_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "question_create", state=MyStates.theme_edit)
def question_create_callback_handler(call: CallbackQuery):
    print(f"{call.message.chat.id} in question create 1")
    bot.set_state(call.from_user.id, MyStates.question_create, call.message.chat.id)
    bot.send_message(call.message.chat.id, "Введите стоимость вопроса:")


@bot.message_handler(state=MyStates.question_create)
def question_create_handler(message: Message):
    print(f"{message.chat.id} in question create 2")
    print(message.text)  # ######################################################
    bot.set_state(message.from_user.id, MyStates.theme_edit, message.chat.id)
    bot.add_data(message.from_user.id, message.chat.id, question=str(uuid1()))
    # bot.send_message(message.chat.id, "Успешно")
    theme_edit_msg_handler(message)


@bot.callback_query_handler(func=lambda call: call.data == "question_delete", state=MyStates.theme_edit)
def question_delete_callback_handler(call: CallbackQuery):
    # list_of_questions = ["100", "200", "300", "400"]
    dict_of_questions = [(1, "100"), (2, "200"), (3, "300"), (4, "400")]
    # dict_of_questions = {"1": "100", "2": "200", "3": "300", "4": "400"}
    markup = InlineKeyboardMarkup(row_width=1)
    for i, value in enumerate(dict_of_questions):
        # markup.add(InlineKeyboardButton(i, callback_data=f"delete_question_{i}"))
        markup.add(InlineKeyboardButton(f"{i}. {value[1]}", callback_data=f"delete_question_{value[0]}"))
    markup.add(InlineKeyboardButton("Назад", callback_data="back_to_theme_edit_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Нажмите, чтобы удалить", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "question_edit", state=MyStates.theme_edit)
def question_edit_list_callback_handler(call: CallbackQuery):
    # list_of_questions = ["100", "200", "300", "400"]
    dict_of_questions = [(1, "100"), (5, "200"), (3, "300"), (4, "400")]
    markup = InlineKeyboardMarkup(row_width=1)
    for i, value in enumerate(dict_of_questions):
        markup.add(InlineKeyboardButton(f"{i}. {value[1]}", callback_data=f"edit_question_{value[0]}"))
    # for i in list_of_questions:
    #     markup.add(InlineKeyboardButton(i, callback_data=f"edit_question_{i}"))
    markup.add(InlineKeyboardButton("Назад", callback_data="back_to_theme_edit_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Нажмите, чтобы редактировать", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_theme_edit_menu", state=MyStates.theme_edit)
def back_menu_question_callback_handler(call: CallbackQuery):
    theme_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_question_"), state=MyStates.theme_edit)
def question_delete_callback_handler(call: CallbackQuery):
    name = call.data[13:]
    print(name)
    # bot.send_message(call.message.chat.id, "Успешно")
    theme_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_question_"), state=MyStates.theme_edit)
def question_edit_callback_handler(call: CallbackQuery):
    bot.set_state(call.from_user.id, MyStates.question_edit, call.message.chat.id)
    name = call.data[14:]
    bot.add_data(call.from_user.id, call.message.chat.id, question=name)
    print(name)
    question_edit_handler(call)


# @bot.message_handler(state=MyStates.question_edit)
def question_edit_handler(call: CallbackQuery):
    markup = quick_markup({
        "Редактировать стоимость": {"callback_data": "_question_cost"},
        "Редактировать ответ": {"callback_data": "_question_answer"},
        "Редактировать вопрос": {"callback_data": "_question_question"},
        "Назад": {"callback_data": "back_to_edit_question_list"}
    }, row_width=1)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        pack_ = data["pack"]
        round_ = data["round"]
        theme_ = data["theme"]
    txt = f"Меню\n\nПак {pack_}\nРаунд {round_}\nТема {theme_}\nРедактирование вопроса"
    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=call.message.chat.id,
                         text=txt, reply_markup=markup)


def question_edit_msg_handler(message: Message):
    markup = quick_markup({
        "Редактировать стоимость": {"callback_data": "_question_cost"},
        "Редактировать ответ": {"callback_data": "_question_answer"},
        "Редактировать вопрос": {"callback_data": "_question_question"},
        "Назад": {"callback_data": "back_to_edit_question_list"}
    }, row_width=1)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        pack_ = data["pack"]
        round_ = data["round"]
        theme_ = data["theme"]
    txt = f"Меню\n\nПак {pack_}\nРаунд {round_}\nТема {theme_}\nРедактирование вопроса"
    try:
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id, text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=message.chat.id,
                         text=txt, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_edit_question_list", state=MyStates.question_edit)
def back_menu_question_callback_handler(call: CallbackQuery):
    bot.set_state(call.from_user.id, MyStates.theme_edit, call.message.chat.id)
    question_edit_list_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "_question_cost", state=MyStates.question_edit)
def question_create_callback_handler(call: CallbackQuery):
    print(f"{call.message.chat.id} in question cost 1")
    bot.set_state(call.from_user.id, MyStates.question_cost, call.message.chat.id)
    bot.send_message(call.message.chat.id, "Введите стоимость вопроса:")


@bot.message_handler(state=MyStates.question_cost)
def question_create_handler(message: Message):
    print(f"{message.chat.id} in question cost 2")
    bot.set_state(message.from_user.id, MyStates.question_edit, message.chat.id)
    bot.add_data(message.from_user.id, message.chat.id, question_cost=message.text)
    # bot.send_message(message.chat.id, "Успешно")
    question_edit_msg_handler(message)


@bot.callback_query_handler(func=lambda call: call.data == "_question_answer", state=MyStates.question_edit)
def question_create_callback_handler(call: CallbackQuery):
    print(f"{call.message.chat.id} in question answer 1")
    bot.set_state(call.from_user.id, MyStates.question_answer, call.message.chat.id)
    bot.send_message(call.message.chat.id, "Введите новый ответ:")


@bot.message_handler(state=MyStates.question_answer)
def question_create_handler(message: Message):
    print(f"{message.chat.id} in question answer 2")
    bot.set_state(message.from_user.id, MyStates.question_edit, message.chat.id)
    bot.add_data(message.from_user.id, message.chat.id, question_ans=message.text)
    # bot.send_message(message.chat.id, "Успешно")
    question_edit_msg_handler(message)


if __name__ == "__main__":
    bot.infinity_polling()
