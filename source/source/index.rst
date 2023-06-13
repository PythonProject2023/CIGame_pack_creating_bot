.. SIGame_pack_creating_bot documentation master file, created by
   sphinx-quickstart on Tue Jun 13 00:51:56 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SIGame_pack_creating_bot's documentation!
====================================================

   - Перед запуском вам необходимо создать своего бота у BotFather в telegram (t.me/BotFather).
   - Получите ключ API вашего нового бота у BotFather.
   - Откройте файл config.py в папке source, вставьте вместо \*Ваш API\* API своего бота

.. code-block:: python

   bot_token = "*Ваш API*"
..

Пример:

.. code-block:: python

   bot_token = "6136842632:AAE9Odc-4fKk73sGJF1H7dqpGuo3Syk"
..

   - У вас должен быть установлен Redis версии >= 4.0 и быть включен на порту 6379
   - Запустите bot.py
   - Вы прекрасны

.. toctree::
   :maxdepth: 0
   :caption: Contents:

   bot_docs
   xml_parser_docs


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
