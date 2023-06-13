"""Telegram bot for creating packs for Your Own Game."""
from telebot import TeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.handler_backends import State, StatesGroup
from telebot.custom_filters import StateFilter
from telebot.storage import StateRedisStorage
from telebot.util import quick_markup
import xml_parser
import config
import os
from l10n import _


bot = TeleBot(config.bot_token, state_storage=StateRedisStorage())
bot.add_custom_filter(StateFilter(bot))


class MyStates(StatesGroup):
    """Class with states."""

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
    question_annotation = State()
    question_cat_cost = State()
    question_cat_theme = State()


@bot.message_handler(commands=["start"])
def start_handler(message: Message):
    """
    Tracking the click on the "start" button.

    Create a user directory where his files and data will be stored.
    """
    print(f"{message.chat.id} in start")
    bot.set_state(message.from_user.id, MyStates.menu_state, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if 'lang' not in data.keys():
            data['lang'] = 'ru'
    xml_parser.CreateUserDirectory(message.chat.id, message.from_user.id)
    menu_handler(message)


# @bot.message_handler(state=MyStates.menu_state)
def menu_handler(message: Message):
    """Display the main menu."""
    print(f"{message.chat.id} in menu")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data['lang']
    markup = quick_markup({
        _("Создать новый пак", lang): {"callback_data": "pack_create"},
        _("Редактировать пак", lang): {"callback_data": "pack_edit"},
        _("Выгрузить пак", lang): {"callback_data": "pack_download"},
        _("Удалить пак", lang): {"callback_data": "pack_delete"},
        _("Смена языка", lang): {"callback_data": "language"}
    }, row_width=1)
    try:
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id, text=_("Меню", lang), reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=message.chat.id,
                         text=_("Меню", lang), reply_markup=markup)


def menu_callback_handler(call: CallbackQuery):
    """Display the main menu."""
    print(f"{call.message.chat.id} in menu")
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    markup = quick_markup({
        _("Создать новый пак", lang): {"callback_data": "pack_create"},
        _("Редактировать пак", lang): {"callback_data": "pack_edit"},
        _("Выгрузить пак", lang): {"callback_data": "pack_download"},
        _("Удалить пак", lang): {"callback_data": "pack_delete"},
        _("Смена языка", lang): {"callback_data": "language"}
    }, row_width=1)
    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text=_("Меню", lang), reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=call.message.chat.id,
                         text=_("Меню", lang), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "language", state=MyStates.menu_state)
def language_callback_handler(call: CallbackQuery):
    """Switch language."""
    print(f"{call.message.chat.id} in lng")
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    if lang == 'ru':
        bot.add_data(call.from_user.id, call.message.chat.id, lang='en')
    else:
        bot.add_data(call.from_user.id, call.message.chat.id, lang='ru')
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    if call.message.text != _("Язык сменен", lang):
        markup = quick_markup({
            _("Создать новый пак", lang): {"callback_data": "pack_create"},
            _("Редактировать пак", lang): {"callback_data": "pack_edit"},
            _("Выгрузить пак", lang): {"callback_data": "pack_download"},
            _("Удалить пак", lang): {"callback_data": "pack_delete"},
            _("Смена языка", lang): {"callback_data": "language"}
        }, row_width=1)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text=_("Язык сменен", lang),
                              reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "pack_create", state=MyStates.menu_state)
def pack_create_callback_handler(call: CallbackQuery):
    """Enter the name of the pack by the user."""
    print(f"{call.message.chat.id} in pack create 1")
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    bot.set_state(call.from_user.id, MyStates.pack_create, call.message.chat.id)
    bot.send_message(call.message.chat.id, _("Введите название пака:", lang))


@bot.message_handler(state=MyStates.pack_create)
def pack_create_handler(message: Message):
    """Create the pack."""
    print(f"{message.chat.id} in pack create 2")
    bot.set_state(message.from_user.id, MyStates.menu_state, message.chat.id)
    xml_parser.CreateNewPack(message.chat.id, message.from_user.id, message.text)
    menu_handler(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("pack_d"), state=MyStates.menu_state)
def pack_download_delete_callback_handler(call: CallbackQuery):
    """Create buttons with pack names for deleting and downloading."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    list_of_packs = xml_parser.GetUserPacks(call.message.chat.id, call.from_user.id)
    markup = InlineKeyboardMarkup(row_width=1)
    if call.data == "pack_delete":
        for i in list_of_packs:
            markup.add(InlineKeyboardButton(i, callback_data=f"delete_pack_{i}"))
        markup.add(InlineKeyboardButton(_("Назад", lang), callback_data="back_to_menu"))
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=_("Нажмите, чтобы удалить", lang), reply_markup=markup)
    elif call.data == "pack_download":
        for i in list_of_packs:
            markup.add(InlineKeyboardButton(i, callback_data=f"download_pack_{i}"))
        markup.add(InlineKeyboardButton(_("Назад", lang), callback_data="back_to_menu"))
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=_("Нажмите, чтобы скачать", lang), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "pack_edit", state=MyStates.menu_state)
def pack_edit_list_callback_handler(call: CallbackQuery):
    """Create buttons with pack names for editing."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    list_of_packs = xml_parser.GetUserPacks(call.message.chat.id, call.from_user.id)
    markup = InlineKeyboardMarkup(row_width=1)
    for i in list_of_packs:
        markup.add(InlineKeyboardButton(i, callback_data=f"edit_pack_{i}"))
    markup.add(InlineKeyboardButton(_("Назад", lang), callback_data="back_to_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=_("Нажмите, чтобы редактировать", lang), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("download_pack_"), state=MyStates.menu_state)
def pack_download_callback_handler(call: CallbackQuery):
    """Download the pack."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    name = call.data[14:]
    try:
        path = xml_parser.LoadPackToSiq(call.message.chat.id, call.from_user.id, name)
        file = open(path, 'rb')
        bot.send_document(call.message.chat.id, file)
        bot.send_message(call.message.chat.id, _("Успешно", lang))
    except Exception as e:
        print(e)
        bot.send_message(call.message.chat.id, _("Ошибка", lang))
    markup = quick_markup({
        _("Создать новый пак", lang): {"callback_data": "pack_create"},
        _("Редактировать пак", lang): {"callback_data": "pack_edit"},
        _("Выгрузить пак", lang): {"callback_data": "pack_download"},
        _("Удалить пак", lang): {"callback_data": "pack_delete"},
        _("Смена языка", lang): {"callback_data": "language"}
    }, row_width=1)
    bot.send_message(chat_id=call.message.chat.id, text=_("Меню", lang), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_pack_"), state=MyStates.menu_state)
def pack_delete_callback_handler(call: CallbackQuery):
    """Delete the pack."""
    name = call.data[12:]
    xml_parser.DeletePack(call.message.chat.id, call.from_user.id, name)
    menu_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu", state=MyStates.menu_state)
def back_menu_callback_handler(call: CallbackQuery):
    """Return to main menu."""
    menu_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_pack_"), state=MyStates.menu_state)
def pack_edit_callback_handler(call: CallbackQuery):
    """Go to edit pack."""
    bot.set_state(call.from_user.id, MyStates.pack_edit, call.message.chat.id)
    name = call.data[10:]
    bot.add_data(call.from_user.id, call.message.chat.id, pack=name)
    final_round_exists = (len(xml_parser.GetRounds(call.message.chat.id, call.from_user.id, final=True)) > 0)
    bot.add_data(call.from_user.id, call.message.chat.id, final_round_exist=final_round_exists)
    pack_edit_handler(call)


# @bot.message_handler(state=MyStates.pack_edit)
def pack_edit_handler(call: CallbackQuery):
    """Display the pack editing menu."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
        pack = data["pack"]
    markup = quick_markup({
        _("Создать финальный раунд", lang): {"callback_data": "round_final_create"},
        _("Создать раунд", lang): {"callback_data": "round_create"},
        _("Редактировать финальный раунд", lang): {"callback_data": "round_final_edit"},
        _("Редактировать раунд", lang): {"callback_data": "round_edit"},
        _("Удалить раунд", lang): {"callback_data": "round_delete"},
        _("Назад", lang): {"callback_data": "back_to_edit_pack_list"}
    }, row_width=1)
    txt = _("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack)
    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=call.message.chat.id,
                         text=txt, reply_markup=markup)


def pack_edit_msg_handler(message: Message):
    """Display the pack editing menu."""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data['lang']
        pack = data["pack"]
    markup = quick_markup({
        _("Создать финальный раунд", lang): {"callback_data": "round_final_create"},
        _("Создать раунд", lang): {"callback_data": "round_create"},
        _("Редактировать финальный раунд", lang): {"callback_data": "round_final_edit"},
        _("Редактировать раунд", lang): {"callback_data": "round_edit"},
        _("Удалить раунд", lang): {"callback_data": "round_delete"},
        _("Назад", lang): {"callback_data": "back_to_edit_pack_list"}
    }, row_width=1)
    txt = _("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack)
    try:
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id,
                              text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=message.chat.id,
                         text=txt, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_edit_pack_list", state=MyStates.pack_edit)
def back_pack_list_callback_handler(call: CallbackQuery):
    """Back to selecting the pack to edit."""
    bot.set_state(call.from_user.id, MyStates.menu_state, call.message.chat.id)
    pack_edit_list_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "round_create", state=MyStates.pack_edit)
def round_create_callback_handler(call: CallbackQuery):
    """Enter the name of the round by the user."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    print(f"{call.message.chat.id} in round create 1")
    bot.set_state(call.from_user.id, MyStates.round_create, call.message.chat.id)
    bot.send_message(call.message.chat.id, _("Введите название раунда:", lang))


@bot.message_handler(state=MyStates.round_create)
def round_create_handler(message: Message):
    """Create the round."""
    print(f"{message.chat.id} in round create 2")
    bot.set_state(message.from_user.id, MyStates.pack_edit, message.chat.id)
    xml_parser.CreateNewRound(message.chat.id, message.from_user.id, message.text)
    pack_edit_msg_handler(message)


@bot.callback_query_handler(func=lambda call: call.data == "round_final_create", state=MyStates.pack_edit)
def round_final_create_callback_handler(call: CallbackQuery):
    """Enter the name of the final round by the user."""
    print(f"{call.message.chat.id} in final round create 1")
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
        exist_ = data["final_round_exist"]
    if exist_:
        bot.send_message(call.message.chat.id, _("Финальный раунд уже существует, сначала удалите старый", lang))
        pack_edit_handler(call)
    else:
        bot.set_state(call.from_user.id, MyStates.round_final_create, call.message.chat.id)
        bot.send_message(call.message.chat.id, _("Введите название финального раунда:", lang))


@bot.message_handler(state=MyStates.round_final_create)
def round_final_create_handler(message: Message):
    """Create the final round."""
    print(f"{message.chat.id} in final round create 2")
    bot.set_state(message.from_user.id, MyStates.pack_edit, message.chat.id)
    xml_parser.CreateNewRound(message.chat.id, message.from_user.id, message.text, final=True)
    bot.add_data(message.from_user.id, message.chat.id, final_round_exist=True)
    pack_edit_msg_handler(message)


@bot.callback_query_handler(func=lambda call: call.data == "round_delete", state=MyStates.pack_edit)
def round_delete_list_callback_handler(call: CallbackQuery):
    """Create buttons with round names for deleting."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    list_of_rounds = xml_parser.GetRounds(call.message.chat.id,
                                          call.from_user.id) + xml_parser.GetRounds(call.message.chat.id,
                                                                                    call.from_user.id, final=True)
    markup = InlineKeyboardMarkup(row_width=1)
    for i in list_of_rounds:
        markup.add(InlineKeyboardButton(i, callback_data=f"delete_round_{i}"))
    markup.add(InlineKeyboardButton(_("Назад", lang), callback_data="back_to_pack_edit_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=_("Нажмите, чтобы удалить", lang), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "round_final_edit", state=MyStates.pack_edit)
def round_final_edit_list_callback_handler(call: CallbackQuery):
    """Create button with final round name for editing and confirming."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    list_of_rounds = xml_parser.GetRounds(call.message.chat.id, call.from_user.id, final=True)
    markup = InlineKeyboardMarkup(row_width=1)
    for i in list_of_rounds:
        markup.add(InlineKeyboardButton(i, callback_data=f"edit_round_f_{i}"))
    markup.add(InlineKeyboardButton(_("Назад", lang), callback_data="back_to_pack_edit_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=_("Нажмите, чтобы редактировать", lang), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "round_edit", state=MyStates.pack_edit)
def round_edit_list_callback_handler(call: CallbackQuery):
    """Create buttons with round names for editing."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    list_of_rounds = xml_parser.GetRounds(call.message.chat.id, call.from_user.id)
    markup = InlineKeyboardMarkup(row_width=1)
    for i in list_of_rounds:
        markup.add(InlineKeyboardButton(i, callback_data=f"edit_round_{i}"))
    markup.add(InlineKeyboardButton(_("Назад", lang), callback_data="back_to_pack_edit_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=_("Нажмите, чтобы редактировать", lang), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_pack_edit_menu", state=MyStates.pack_edit)
def back_pack_menu_callback_handler(call: CallbackQuery):
    """Back to pack editing menu."""
    pack_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_round_"), state=MyStates.pack_edit)
def round_delete_callback_handler(call: CallbackQuery):
    """Delete the round."""
    name = call.data[13:]
    xml_parser.DeleteRound(call.message.chat.id, call.from_user.id, name)
    pack_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_round_f_"), state=MyStates.pack_edit)
def round_final_edit_callback_handler(call: CallbackQuery):
    """Go to edit final round."""
    bot.set_state(call.from_user.id, MyStates.round_edit, call.message.chat.id)
    name = call.data[13:]
    bot.add_data(call.from_user.id, call.message.chat.id, round=name, final=True)
    round_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_round_"), state=MyStates.pack_edit)
def round_edit_callback_handler(call: CallbackQuery):
    """Go to edit round."""
    bot.set_state(call.from_user.id, MyStates.round_edit, call.message.chat.id)
    name = call.data[11:]
    bot.add_data(call.from_user.id, call.message.chat.id, round=name, final=False)
    round_edit_handler(call)


# @bot.message_handler(state=MyStates.round_edit)
def round_edit_handler(call: CallbackQuery):
    """Display the round editing menu."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
        pack_ = data["pack"]
        round_ = data["round"]
        final_ = data["final"]
    markup = quick_markup({
        _("Создать тему", lang): {"callback_data": "theme_create"},
        _("Редактировать тему", lang): {"callback_data": "theme_edit"},
        _("Удалить тему", lang): {"callback_data": "theme_delete"},
        _("Назад", lang): {"callback_data": "back_to_edit_round_list"}
    }, row_width=1)
    if final_:
        txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) +
               "\n" + _("Финальный раунд {}", lang).format(round_))
    else:
        txt = _("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" + _("Pаунд {}", lang).format(round_)
    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=call.message.chat.id,
                         text=txt, reply_markup=markup)


def round_edit_msg_handler(message: Message):
    """Display the round editing menu."""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data['lang']
        pack_ = data["pack"]
        round_ = data["round"]
        final_ = data["final"]
    markup = quick_markup({
        _("Создать тему", lang): {"callback_data": "theme_create"},
        _("Редактировать тему", lang): {"callback_data": "theme_edit"},
        _("Удалить тему", lang): {"callback_data": "theme_delete"},
        _("Назад", lang): {"callback_data": "back_to_edit_round_list"}
    }, row_width=1)
    if final_:
        txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) +
               "\n" + _("Финальный раунд {}", lang).format(round_))
    else:
        txt = _("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" + _("Pаунд {}", lang).format(round_)
    try:
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id, text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=message.chat.id,
                         text=txt, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_edit_round_list", state=MyStates.round_edit)
def back_round_list_callback_handler(call: CallbackQuery):
    """Back to selecting the round to edit."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        final_ = data["final"]
    bot.set_state(call.from_user.id, MyStates.pack_edit, call.message.chat.id)
    if final_:
        round_final_edit_list_callback_handler(call)
    else:
        round_edit_list_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "theme_create", state=MyStates.round_edit)
def theme_create_callback_handler(call: CallbackQuery):
    """Enter the name of the theme by the user."""
    print(f"{call.message.chat.id} in theme create 1")
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    bot.set_state(call.from_user.id, MyStates.theme_create, call.message.chat.id)
    bot.send_message(call.message.chat.id, _("Введите название темы:", lang))


@bot.message_handler(state=MyStates.theme_create)
def theme_create_handler(message: Message):
    """Create the theme."""
    print(f"{message.chat.id} in theme create 2")
    bot.set_state(message.from_user.id, MyStates.round_edit, message.chat.id)
    bot.add_data(message.from_user.id, message.chat.id, theme=message.text)
    xml_parser.CreateNewTheme(message.chat.id, message.from_user.id, message.text)
    round_edit_msg_handler(message)


@bot.callback_query_handler(func=lambda call: call.data == "theme_delete", state=MyStates.round_edit)
def theme_delete_list_callback_handler(call: CallbackQuery):
    """Create buttons with theme names for deleting."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    list_of_theme = xml_parser.GetThemes(call.message.chat.id, call.from_user.id)
    markup = InlineKeyboardMarkup(row_width=1)
    for i in list_of_theme:
        markup.add(InlineKeyboardButton(i, callback_data=f"delete_theme_{i}"))
    markup.add(InlineKeyboardButton(_("Назад", lang), callback_data="back_to_round_edit_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=_("Нажмите, чтобы удалить", lang), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "theme_edit", state=MyStates.round_edit)
def theme_edit_list_callback_handler(call: CallbackQuery):
    """Create buttons with theme names for editing."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    list_of_theme = xml_parser.GetThemes(call.message.chat.id, call.from_user.id)
    markup = InlineKeyboardMarkup(row_width=1)
    for i in list_of_theme:
        markup.add(InlineKeyboardButton(i, callback_data=f"edit_theme_{i}"))
    markup.add(InlineKeyboardButton(_("Назад", lang), callback_data="back_to_round_edit_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=_("Нажмите, чтобы редактировать", lang), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_round_edit_menu", state=MyStates.round_edit)
def back_menu_theme_callback_handler(call: CallbackQuery):
    """Back to round editing menu."""
    round_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_theme_"), state=MyStates.round_edit)
def theme_delete_callback_handler(call: CallbackQuery):
    """Delete the theme."""
    name = call.data[13:]
    xml_parser.DeleteTheme(call.message.chat.id, call.from_user.id, name)
    round_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_theme_"), state=MyStates.round_edit)
def theme_edit_callback_handler(call: CallbackQuery):
    """Go to edit theme."""
    bot.set_state(call.from_user.id, MyStates.theme_edit, call.message.chat.id)
    name = call.data[11:]
    bot.add_data(call.from_user.id, call.message.chat.id, theme=name)
    final_question_exists = (len(xml_parser.GetQuestions(call.message.chat.id, call.from_user.id)) > 0)
    bot.add_data(call.from_user.id, call.message.chat.id, final_quest_exist=final_question_exists)
    theme_edit_handler(call)


# @bot.message_handler(state=MyStates.theme_edit)
def theme_edit_handler(call: CallbackQuery):
    """Display the theme editing menu."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
        pack_ = data["pack"]
        round_ = data["round"]
        theme_ = data["theme"]
        final_ = data["final"]
    markup = quick_markup({
        _("Создать вопрос", lang): {"callback_data": "question_create"},
        _("Редактировать вопрос", lang): {"callback_data": "question_edit"},
        _("Удалить вопрос", lang): {"callback_data": "question_delete"},
        _("Назад", lang): {"callback_data": "back_to_edit_theme_list"}
    }, row_width=1)
    if final_:
        txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" +
               _("Финальный раунд {}", lang).format(round_) + "\n" + _("Тема {}", lang).format(theme_))
    else:
        txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" +
               _("Раунд {}", lang).format(round_) + "\n" + _("Тема {}", lang).format(theme_))
    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=call.message.chat.id,
                         text=txt, reply_markup=markup)


def theme_edit_msg_handler(message: Message):
    """Display the theme editing menu."""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data['lang']
        pack_ = data["pack"]
        round_ = data["round"]
        theme_ = data["theme"]
        final_ = data["final"]
    markup = quick_markup({
        _("Создать вопрос", lang): {"callback_data": "question_create"},
        _("Редактировать вопрос", lang): {"callback_data": "question_edit"},
        _("Удалить вопрос", lang): {"callback_data": "question_delete"},
        _("Назад", lang): {"callback_data": "back_to_edit_theme_list"}
    }, row_width=1)
    if final_:
        txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" +
               _("Финальный раунд {}", lang).format(round_) + "\n" + _("Тема {}", lang).format(theme_))
    else:
        txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" +
               _("Раунд {}", lang).format(round_) + "\n" + _("Тема {}", lang).format(theme_))
    try:
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id, text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=message.chat.id,
                         text=txt, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_edit_theme_list", state=MyStates.theme_edit)
def back_theme_list_callback_handler(call: CallbackQuery):
    """Back to selecting the theme to edit."""
    bot.set_state(call.from_user.id, MyStates.round_edit, call.message.chat.id)
    theme_edit_list_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "question_create", state=MyStates.theme_edit)
def question_create_callback_handler(call: CallbackQuery):
    """
    Enter the cost of the question by the user.

    If the round is final, then create the question.
    """
    print(f"{call.message.chat.id} in question create 1")
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
        final_ = data["final"]
        exist_ = data["final_quest_exist"]
    if final_ and exist_:
        bot.send_message(call.message.chat.id,
                         _("Вопрос в теме финального раунда уже существует, сначала удалите старый", lang))
        theme_edit_handler(call)
    elif final_:
        xml_parser.CreateNewQuestion(call.message.chat.id, call.from_user.id, 0)
        bot.add_data(call.from_user.id, call.message.chat.id, final_quest_exist=True)
    else:
        bot.set_state(call.from_user.id, MyStates.question_create, call.message.chat.id)
        bot.send_message(call.message.chat.id, _("Введите стоимость вопроса:", lang))


def question_create_msg_handler(message: Message):
    """
    Enter the cost of the question by the user.

    If the round is final, then create the question.
    """
    print(f"{message.chat.id} in question create 1")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data['lang']
        final_ = data["final"]
        exist_ = data["final_quest_exist"]
    if final_ and exist_:
        bot.send_message(message.chat.id, _("Вопрос в теме финального раунда уже существует, сначала удалите старый",
                                            lang))
        theme_edit_msg_handler(message)
    elif final_:
        xml_parser.CreateNewQuestion(message.chat.id, message.from_user.id, 0)
        bot.add_data(message.from_user.id, message.chat.id, final_quest_exist=True)
    else:
        bot.set_state(message.from_user.id, MyStates.question_create, message.chat.id)
        bot.send_message(message.chat.id, _("Введите стоимость вопроса:", lang))


@bot.message_handler(state=MyStates.question_create)
def question_create_handler(message: Message):
    """Create the question."""
    print(f"{message.chat.id} in question create 2")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data['lang']
    try:
        price = xml_parser.CheckPrice(message.text)
        xml_parser.CreateNewQuestion(message.chat.id, message.from_user.id, price)
        bot.set_state(message.from_user.id, MyStates.theme_edit, message.chat.id)
        theme_edit_msg_handler(message)
    except ValueError:
        bot.send_message(message.chat.id, _("Введите число", lang))
        question_create_msg_handler(message)


@bot.callback_query_handler(func=lambda call: call.data == "question_delete", state=MyStates.theme_edit)
def question_delete_list_callback_handler(call: CallbackQuery):
    """
    Create buttons with question cost for deleting.

    If the round is final and the question exists, then create button with "Final round" text.
    """
    dict_of_questions = xml_parser.GetQuestions(call.message.chat.id, call.from_user.id)
    markup = InlineKeyboardMarkup(row_width=1)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
        final_ = data["final"]
        exist_ = data["final_quest_exist"]
    if final_ and exist_:
        for value in dict_of_questions:
            markup.add(InlineKeyboardButton(_("Финальный вопрос", lang), callback_data=f"delete_question_{value[0]}"))
    else:
        for i, value in enumerate(dict_of_questions, start=1):
            markup.add(InlineKeyboardButton(f"{i}. {value[1]}", callback_data=f"delete_question_{value[0]}"))
    markup.add(InlineKeyboardButton(_("Назад", lang), callback_data="back_to_theme_edit_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=_("Нажмите, чтобы удалить", lang), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "question_edit", state=MyStates.theme_edit)
def question_edit_list_callback_handler(call: CallbackQuery):
    """
    Create buttons with question cost for editing.

    If the round is final and the question exists, then create button with "Final round" text.
    """
    dict_of_questions = xml_parser.GetQuestions(call.message.chat.id, call.from_user.id)
    markup = InlineKeyboardMarkup(row_width=1)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
        final_ = data["final"]
        exist_ = data["final_quest_exist"]
    if final_ and exist_:
        for value in dict_of_questions:
            markup.add(InlineKeyboardButton(_("Финальный вопрос", lang), callback_data=f"edit_question_{value[0]}"))
    else:
        for i, value in enumerate(dict_of_questions, start=1):
            markup.add(InlineKeyboardButton(f"{i}. {value[1]}", callback_data=f"edit_question_{value[0]}"))
    markup.add(InlineKeyboardButton(_("Назад", lang), callback_data="back_to_theme_edit_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=_("Нажмите, чтобы редактировать", lang), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_theme_edit_menu", state=MyStates.theme_edit)
def back_menu_question_callback_handler(call: CallbackQuery):
    """Back to theme editing menu."""
    theme_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_question_"), state=MyStates.theme_edit)
def question_delete_callback_handler(call: CallbackQuery):
    """Delete the question."""
    uid = call.data[16:]
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        final_ = data["final"]
    if final_:
        bot.add_data(call.from_user.id, call.message.chat.id, final_quest_exist=False)
    xml_parser.DeleteQuestion(call.message.chat.id, call.from_user.id, uid)
    theme_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_question_"), state=MyStates.theme_edit)
def question_edit_callback_handler(call: CallbackQuery):
    """Go to edit question."""
    bot.set_state(call.from_user.id, MyStates.question_edit, call.message.chat.id)
    name = call.data[14:]
    bot.add_data(call.from_user.id, call.message.chat.id, question=name)
    question_edit_handler(call)


# @bot.message_handler(state=MyStates.question_edit)
def question_edit_handler(call: CallbackQuery):
    """Display the question editing menu."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
        pack_ = data["pack"]
        round_ = data["round"]
        theme_ = data["theme"]
        final_ = data["final"]
    if final_:
        markup = quick_markup({
            _("Редактировать ответ", lang): {"callback_data": "_question_answer"},
            _("Редактировать вопрос", lang): {"callback_data": "_question_question"},
            _("Посмотреть вопрос", lang): {"callback_data": "_question_view"},
            _("Редактировать пояснение", lang): {"callback_data": "_question_annotation"},
            _("Удалить пояснение", lang): {"callback_data": "_question_annotation_delete"},
            _("Назад", lang): {"callback_data": "back_to_edit_question_list"}
        }, row_width=1)
    else:
        markup = quick_markup({
            _("Редактировать стоимость", lang): {"callback_data": "_question_cost"},
            _("Редактировать ответ", lang): {"callback_data": "_question_answer"},
            _("Редактировать вопрос", lang): {"callback_data": "_question_question"},
            _("Посмотреть вопрос", lang): {"callback_data": "_question_view"},
            _("Редактировать пояснение", lang): {"callback_data": "_question_annotation"},
            _("Удалить пояснение", lang): {"callback_data": "_question_annotation_delete"},
            _("Изменить тип вопроса", lang): {"callback_data": "_question_type"},
            _("Назад", lang): {"callback_data": "back_to_edit_question_list"}
        }, row_width=1)
    ans = xml_parser.GetQuestionAnswer(call.message.chat.id, call.from_user.id)
    annotation = xml_parser.GetQuestionComment(call.message.chat.id, call.from_user.id)
    if final_:
        if ans is None:
            txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" +
                   _("Финальный раунд {}", lang).format(round_) + "\n" +
                   _("Тема {}", lang).format(theme_) + "\n" + _("Редактирование вопроса", lang))
        else:
            txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" +
                   _("Финальный раунд {}", lang).format(round_) + "\n" +
                   _("Тема {}", lang).format(theme_) + "\n" + _("Редактирование вопроса", lang) + "\n" +
                   _("Ответ: {}", lang).format(ans))
    else:
        cost = xml_parser.GetQuestionPrice(call.message.chat.id, call.from_user.id)
        if ans is None:
            txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" +
                   _("Раунд {}", lang).format(round_) + "\n" +
                   _("Тема {}", lang).format(theme_) + "\n" +
                   _("Редактирование вопроса {}", lang).format(cost))
        else:
            txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" +
                   _("Раунд {}", lang).format(round_) + "\n" +
                   _("Тема {}", lang).format(theme_) + "\n" +
                   _("Редактирование вопроса {}", lang).format(cost) + "\n" +
                   _("Ответ: {}", lang).format(ans))
    if annotation is not None:
        txt += "\n" + _("Пояснение: {}", lang).format(annotation)
    if not final_:
        quest_type = xml_parser.GetQuestionType(call.message.chat.id, call.from_user.id)
        if quest_type['type'] != 'usual':
            txt += '\n' + _('Тип вопроса: ', lang)
            if quest_type['type'] == 'cat':
                real_cost = quest_type['cost']
                real_theme = quest_type['theme']
                txt += (_('Кот в мешке {}', lang).format(real_cost) + '\n' +
                        _('Настоящая тема: {}', lang).format(real_theme))
            elif quest_type['type'] == 'risk':
                txt += _('Вопрос без риска', lang)
    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=call.message.chat.id,
                         text=txt, reply_markup=markup)


def question_edit_msg_handler(message: Message):
    """Display the question editing menu."""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data['lang']
        pack_ = data["pack"]
        round_ = data["round"]
        theme_ = data["theme"]
        final_ = data["final"]
    if final_:
        markup = quick_markup({
            _("Редактировать ответ", lang): {"callback_data": "_question_answer"},
            _("Редактировать вопрос", lang): {"callback_data": "_question_question"},
            _("Посмотреть вопрос", lang): {"callback_data": "_question_view"},
            _("Редактировать пояснение", lang): {"callback_data": "_question_annotation"},
            _("Удалить пояснение", lang): {"callback_data": "_question_annotation_delete"},
            _("Назад", lang): {"callback_data": "back_to_edit_question_list"}
        }, row_width=1)
    else:
        markup = quick_markup({
            _("Редактировать стоимость", lang): {"callback_data": "_question_cost"},
            _("Редактировать ответ", lang): {"callback_data": "_question_answer"},
            _("Редактировать вопрос", lang): {"callback_data": "_question_question"},
            _("Посмотреть вопрос", lang): {"callback_data": "_question_view"},
            _("Редактировать пояснение", lang): {"callback_data": "_question_annotation"},
            _("Удалить пояснение", lang): {"callback_data": "_question_annotation_delete"},
            _("Изменить тип вопроса", lang): {"callback_data": "_question_type"},
            _("Назад", lang): {"callback_data": "back_to_edit_question_list"}
        }, row_width=1)
    ans = xml_parser.GetQuestionAnswer(message.chat.id, message.from_user.id)
    annotation = xml_parser.GetQuestionComment(message.chat.id, message.from_user.id)
    if final_:
        if ans is None:
            txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" +
                   _("Финальный раунд {}", lang).format(round_) + "\n" +
                   _("Тема {}", lang).format(theme_) + "\n" + _("Редактирование вопроса", lang))
        else:
            txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" +
                   _("Финальный раунд {}", lang).format(round_) + "\n" +
                   _("Тема {}", lang).format(theme_) + "\n" + _("Редактирование вопроса", lang) + "\n" +
                   _("Ответ: {}", lang).format(ans))
    else:
        cost = xml_parser.GetQuestionPrice(message.chat.id, message.from_user.id)
        if ans is None:
            txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" +
                   _("Раунд {}", lang).format(round_) + "\n" +
                   _("Тема {}", lang).format(theme_) + "\n" +
                   _("Редактирование вопроса {}", lang).format(cost))
        else:
            txt = (_("Меню", lang) + "\n\n" + _("Пак {}", lang).format(pack_) + "\n" +
                   _("Раунд {}", lang).format(round_) + "\n" +
                   _("Тема {}", lang).format(theme_) + "\n" +
                   _("Редактирование вопроса {}", lang).format(cost) + "\n" +
                   _("Ответ: {}", lang).format(ans))
    if annotation is not None:
        txt += "\n" + _("Пояснение: {}", lang).format(annotation)
    if not final_:
        quest_type = xml_parser.GetQuestionType(message.chat.id, message.from_user.id)
        if quest_type['type'] != 'usual':
            txt += '\n' + _('Тип вопроса: ', lang)
            if quest_type['type'] == 'cat':
                real_cost = quest_type['cost']
                real_theme = quest_type['theme']
                txt += (_('Кот в мешке {}', lang).format(real_cost) + '\n' +
                        _('Настоящая тема: {}', lang).format(real_theme))
            elif quest_type['type'] == 'risk':
                txt += _('Вопрос без риска', lang)
    try:
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id, text=txt, reply_markup=markup)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=message.chat.id,
                         text=txt, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_edit_question_list", state=MyStates.question_edit)
def back_question_list_callback_handler(call: CallbackQuery):
    """Back to selecting the question to edit."""
    bot.set_state(call.from_user.id, MyStates.theme_edit, call.message.chat.id)
    question_edit_list_callback_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "_question_view", state=MyStates.question_edit)
def question_view_callback_handler(call: CallbackQuery):
    """View the question."""
    obj, type_obj = xml_parser.GetQuestionForm(call.message.chat.id, call.from_user.id)
    if type_obj == "text":
        bot.send_message(call.message.chat.id, obj)
    elif type_obj == "file":
        file = open(obj, 'rb')
        if obj[-3:] == "png":
            bot.send_photo(call.message.chat.id, file)
        elif obj[-3:] == "ogg":
            bot.send_audio(call.message.chat.id, file)
        elif obj[-3:] == "mp4":
            bot.send_video(call.message.chat.id, file)
    question_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "_question_annotation_delete", state=MyStates.question_edit)
def question_annotation_delete_callback_handler(call: CallbackQuery):
    """Delete the annotation of the question."""
    xml_parser.DeleteQuestionComment(call.message.chat.id, call.from_user.id)
    question_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "_question_annotation", state=MyStates.question_edit)
def question_annotation_callback_handler(call: CallbackQuery):
    """Enter the annotation of the question by the user."""
    print(f"{call.message.chat.id} in question annotation 1")
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    bot.set_state(call.from_user.id, MyStates.question_annotation, call.message.chat.id)
    bot.send_message(call.message.chat.id, _("Введите пояснение к вопросу:", lang))


def question_annotation_msg_handler(message: Message):
    """Enter the annotation of the question by the user."""
    print(f"{message.chat.id} in question annotation 1")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data['lang']
    bot.set_state(message.from_user.id, MyStates.question_annotation, message.chat.id)
    bot.send_message(message.chat.id, _("Введите пояснение к вопросу:", lang))


@bot.message_handler(state=MyStates.question_annotation)
def question_annotation_handler(message: Message):
    """Edit question annotation."""
    print(f"{message.chat.id} in question annotation 2")
    xml_parser.SetQuestionComment(message.chat.id, message.from_user.id, message.text)
    bot.set_state(message.from_user.id, MyStates.question_edit, message.chat.id)
    question_edit_msg_handler(message)


@bot.callback_query_handler(func=lambda call: call.data == "_question_cost", state=MyStates.question_edit)
def question_cost_callback_handler(call: CallbackQuery):
    """Enter the cost of the question by the user."""
    print(f"{call.message.chat.id} in question cost 1")
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    bot.set_state(call.from_user.id, MyStates.question_cost, call.message.chat.id)
    bot.send_message(call.message.chat.id, _("Введите стоимость вопроса:", lang))


def question_cost_msg_handler(message: Message):
    """Enter the cost of the question by the user."""
    print(f"{message.chat.id} in question cost 1")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data['lang']
    bot.set_state(message.from_user.id, MyStates.question_cost, message.chat.id)
    bot.send_message(message.chat.id, _("Введите стоимость вопроса:", lang))


@bot.message_handler(state=MyStates.question_cost)
def question_cost_handler(message: Message):
    """Edit question cost."""
    print(f"{message.chat.id} in question cost 2")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data['lang']
    bot.set_state(message.from_user.id, MyStates.question_edit, message.chat.id)
    try:
        price = xml_parser.CheckPrice(message.text)
        xml_parser.SetQuestionPrice(message.chat.id, message.from_user.id, price)
        question_edit_msg_handler(message)
    except ValueError:
        bot.send_message(message.chat.id, _("Введите число", lang))
        question_cost_msg_handler(message)


@bot.callback_query_handler(func=lambda call: call.data == "_question_answer", state=MyStates.question_edit)
def question_answer_callback_handler(call: CallbackQuery):
    """Enter the cost of the question by the user."""
    print(f"{call.message.chat.id} in question answer 1")
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    bot.set_state(call.from_user.id, MyStates.question_answer, call.message.chat.id)
    bot.send_message(call.message.chat.id, _("Введите новый ответ:", lang))


@bot.message_handler(state=MyStates.question_answer)
def question_answer_handler(message: Message):
    """Add answer to question."""
    print(f"{message.chat.id} in question answer 2")
    bot.set_state(message.from_user.id, MyStates.question_edit, message.chat.id)
    xml_parser.SetQuestionAnswer(message.chat.id, message.from_user.id, message.text)
    question_edit_msg_handler(message)


@bot.callback_query_handler(func=lambda call: call.data == "_question_question", state=MyStates.question_edit)
def question_question_handler(call: CallbackQuery):
    """Send file or text by user."""
    print(f"{call.message.chat.id} in question question 1")
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    bot.set_state(call.from_user.id, MyStates.question_question, call.message.chat.id)
    bot.send_message(call.message.chat.id,
                     _("Введите вопрос или отправьте файл\nПоддерживаются фото, видео, кружочки, аудио, голосовые",
                       lang))


@bot.message_handler(content_types=['photo', 'audio', 'video', 'voice', 'video_note', 'text'],
                     state=MyStates.question_question)
def file_handler(message: Message):
    """Add file or text to question."""
    print(f"{message.chat.id} in question question 2")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        pack_ = data["pack"]
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        if not os.path.exists(f"../packs/{message.chat.id}/{pack_}/.files/"):
            os.makedirs(f"../packs/{message.chat.id}/{pack_}/.files/")
        src = f"../packs/{message.chat.id}/{pack_}/.files/" + message.photo[1].file_id + ".png"
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        xml_parser.SetQuestionFile(message.chat.id,
                                   message.from_user.id,
                                   f"../packs/{message.chat.id}/{pack_}/.files/" + message.photo[1].file_id + ".png",
                                   "image")
    elif message.content_type == 'audio':
        file_info = bot.get_file(message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        if not os.path.exists(f"../packs/{message.chat.id}/{pack_}/.files/"):
            os.makedirs(f"../packs/{message.chat.id}/{pack_}/.files/")
        src = f"../packs/{message.chat.id}/{pack_}/.files/" + message.audio.file_id + ".ogg"
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        xml_parser.SetQuestionFile(message.chat.id,
                                   message.from_user.id,
                                   f"../packs/{message.chat.id}/{pack_}/.files/" + message.audio.file_id + ".ogg",
                                   "audio")
    elif message.content_type == 'voice':
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        if not os.path.exists(f"../packs/{message.chat.id}/{pack_}/.files/"):
            os.makedirs(f"../packs/{message.chat.id}/{pack_}/.files/")
        src = f"../packs/{message.chat.id}/{pack_}/.files/" + message.voice.file_id + ".ogg"
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        xml_parser.SetQuestionFile(message.chat.id,
                                   message.from_user.id,
                                   f"../packs/{message.chat.id}/{pack_}/.files/" + message.voice.file_id + ".ogg",
                                   "audio")
    elif message.content_type == 'video':
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        if not os.path.exists(f"../packs/{message.chat.id}/{pack_}/.files/"):
            os.makedirs(f"../packs/{message.chat.id}/{pack_}/.files/")
        src = f"../packs/{message.chat.id}/{pack_}/.files/" + message.video.file_id + ".mp4"
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        xml_parser.SetQuestionFile(message.chat.id,
                                   message.from_user.id,
                                   f"../packs/{message.chat.id}/{pack_}/.files/" + message.video.file_id + ".mp4",
                                   "video")
    elif message.content_type == 'video_note':
        file_info = bot.get_file(message.video_note.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        if not os.path.exists(f"../packs/{message.chat.id}/{pack_}/.files/"):
            os.makedirs(f"../packs/{message.chat.id}/{pack_}/.files/")
        src = f"../packs/{message.chat.id}/{pack_}/.files/" + message.video_note.file_id + ".mp4"
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        xml_parser.SetQuestionFile(message.chat.id,
                                   message.from_user.id,
                                   f"../packs/{message.chat.id}/{pack_}/.files/" + message.video_note.file_id + ".mp4",
                                   "video")
    elif message.content_type == 'text':
        xml_parser.SetQuestionText(message.chat.id, message.from_user.id, message.text)
    bot.set_state(message.from_user.id, MyStates.question_edit, message.chat.id)
    question_edit_msg_handler(message)


@bot.callback_query_handler(func=lambda call: call.data == "_question_type", state=MyStates.question_edit)
def question_type_list_callback_handler(call: CallbackQuery):
    """Create buttons with types of question."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    markup = quick_markup({
        _("Обычный вопрос", lang): {"callback_data": "_question_type_common"},
        _("Кот в мешке", lang): {"callback_data": "_question_type_cat"},
        _("Вопрос без риска", lang): {"callback_data": "_question_type_risk"},
        _("Назад", lang): {"callback_data": "back_to_question_menu"}
    }, row_width=1)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=_("Выберите тип", lang), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_question_menu", state=MyStates.question_edit)
def back_to_question_menu_callback_handler(call: CallbackQuery):
    """Back to question menu."""
    question_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "_question_type_common", state=MyStates.question_edit)
def question_type_common_callback_handler(call: CallbackQuery):
    """Set question type to common."""
    xml_parser.SetQuestionType(call.message.chat.id, call.from_user.id, 'usual')
    question_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "_question_type_risk", state=MyStates.question_edit)
def question_type_risk_callback_handler(call: CallbackQuery):
    """Set question type to no risk."""
    xml_parser.SetQuestionType(call.message.chat.id, call.from_user.id, 'risk')
    question_edit_handler(call)


@bot.callback_query_handler(func=lambda call: call.data == "_question_type_cat", state=MyStates.question_edit)
def question_type_cat_callback_handler(call: CallbackQuery):
    """Enter cost of cat question."""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        lang = data['lang']
    bot.set_state(call.from_user.id, MyStates.question_cat_cost, call.message.chat.id)
    bot.send_message(call.message.chat.id, _("Введите стоимость вопроса:", lang))


def question_type_cat_msg_handler(message: Message):
    """Enter cost of cat question."""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data['lang']
    bot.set_state(message.from_user.id, MyStates.question_cat_cost, message.chat.id)
    bot.send_message(message.chat.id, _("Введите стоимость вопроса:", lang))


@bot.message_handler(state=MyStates.question_cat_cost)
def question_cat_cost_handler(message: Message):
    """Save cat question cost."""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data['lang']
    try:
        price = xml_parser.CheckPrice(message.text)
        bot.set_state(message.from_user.id, MyStates.question_cat_theme, message.chat.id)
        bot.add_data(message.from_user.id, message.chat.id, cat_price=price)
        bot.send_message(message.chat.id, _("Введите тему вопроса:", lang))
    except ValueError:
        bot.set_state(message.from_user.id, MyStates.question_edit, message.chat.id)
        bot.send_message(message.chat.id, _("Введите число", lang))
        question_type_cat_msg_handler(message)


@bot.message_handler(state=MyStates.question_cat_theme)
def question_cat_theme_handler(message: Message):
    """Edit cat question theme."""
    bot.set_state(message.from_user.id, MyStates.question_edit, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        price_ = data["cat_price"]
    xml_parser.SetQuestionType(message.chat.id, message.from_user.id, 'cat', message.text, price_)
    question_edit_msg_handler(message)


if __name__ == "__main__":
    bot.infinity_polling()
