import logging      # подключаем библиотеку логгинга
import time         # подключаем библиотеку для работы с временем
import requests     # подключаем HTTP библиотеку для работы с сайтами
import telebot      # подключаем библиотеку TelegramBotAPI для работы с API telegram
from telebot import types

# import os
import news_parser_Open  # подключаем модуль парсера новостных сайтов

token = "2075481312:AAFSqpJD4jTdtHTYx8Pepl6YVSa0RhY2uPI"#second bot (@starsfromdeliverybot)
id_chan = "-1001592062496"#chat 'Открытия'

logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

count_err = 0  # обнуляем счетчик ошибок связи
mute_on = False     # запрет отправлять сообщения в канал

bot = telebot.TeleBot(token)  # создаем экземпляр класса TeleBot
"""
После этого объявления нам нужно зарегистрировать обработчики сообщений. 


Обработчики сообщений определяют фильтры, которые сообщение должно пройти. 
Если сообщение проходит фильтр, вызывается декорированная функция и входящее сообщ. передается в качестве аргумента.

Функция, оформленная обработчиком сообщений, может иметь произвольное имя, 
однако у нее должен быть только один параметр (message).

message – это объект из Bot API, содержащий в себе информацию о сообщении. Полезные поля:
message.chat.id – идентификатор чата
message.from.id – идентификатор пользователя
message.text – текст сообщения

Примечание: все обработчики тестируются в том порядке, в котором они были объявлены.
"""


# Декоратор @message_handler реагирует на входящие сообщение
@bot.message_handler(commands=['start'])  # реакция только на команду /start
def start(message):  # выполняется при запуске бота:
    id_chat = message.chat.id
    # Функция send_message принимает идентификатор чата и текст для отправки в качестве обязательных аргументов
    bot.send_message(id_chat, "Добре!")  # отправка сообщения в ответ на команду
    # bot.send_message(id_chan, "Бот \"%s\" был перезапущен администратором." %
    #                           os.path.basename(__file__).split('.py')[0])  # отправка сообщения в канал
    if mute_on is False:
        bot.send_message(id_chan, "Де ви знову взялися на мою голову")
        # photo_url = "https://funart.pro/uploads/posts/2021-07/1626583481_6-funart-pro-p-smeshnie-koti-do-slez-zhivotnie-krasivo-fo-11.jpg"
        # bot.send_photo(id_chan, photo=photo_url, caption="Я проснулся!")
    # функция send_photo для отправки изображений из локального хранилища или по ссылке
    # bot.send_photo(message.chat.id, photo=photo_url, caption='It works!')

    while True:
        count_post = 0  # счетчик отправленных постов
        file_w = open(news_parser_Open.base_file, 'w')
        for i in range(news_parser_Open.count):  # Отправка постов с новостями
            post_text = news_parser_Open.get_post(i)
            if not mute_on:     # 05/04 добавил мутирование
                if post_text[0] is not None:  # условие отправки
                    bot.send_message(id_chan, post_text[0], disable_web_page_preview=True)
                    count_post += 1  # инкрементируем счетчик отправленных постов в этом цикле

            file_w.write(str(news_parser_Open.site[i][1]) + '\n')
        file_w.close()

        sleep_t = 600  # интервал проверки сайтов и отправки сообщений в Telegram

        # now = datetime.now().time()  # time object
        # print("now =", now)

        t = time.localtime()
        current_t = time.strftime("%H:%M:%S", t)
        print("%s - Відпрацьовано через %d сек. з запуску, далі спимо %d сек. Всього нових: %d шт. в даному циклі" %
              (current_t, time.perf_counter(), sleep_t, count_post))
        # print("Всього нових %d шт. в даному циклі" % count_post)

        time.sleep(sleep_t)  # засыпаем на xx минут


@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, f"Поточний файл:\n"
    f"{news_parser_Open.site[0][0]}, {news_parser_Open.site[0][1]}\n",
                     disable_web_page_preview=True)


@bot.message_handler(commands=['mute'])
def mute(message):
    global mute_on  # Указание, что необходимо изменить глобальную копию mute_on
    mute_on = not mute_on
    if mute_on:
        bot.send_message(message.chat.id, "Заборонена відправка до каналу")
    else:
        bot.send_message(message.chat.id, "Дозволена відправка до каналу")


@bot.message_handler(content_types=["text"])  # реакция на любой текст, если это не были команды выше
def command_bot(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_a = types.KeyboardButton('/start')
    button_b = types.KeyboardButton('/info')
    button_c = types.KeyboardButton('/mute')

    markup.row(button_a, button_b, button_c)

    bot.send_message(message.chat.id, 'Обери команду\n'
                                      '/start - почати цикл з початку (після запуску боту)\n'
                                      '/info - поточний файл з ID новин\n'
                                      '/mute - зміна дозволу відправки в канал (інверсія)', reply_markup=markup)


# У метода bot.polling есть параметр none_stop, который по умолчанию равен False
# Если данный параметр равен True, то бот не будет останавливаться при какой-либо ошибке
# bot.polling(none_stop=True)

# PS: всегда используйте infinity_polling или свой собственный цикл бесконечности с обработчиком исключений...
# bot.infinity_polling(logger_level=logging.DEBUG, timeout=10, long_polling_timeout=5)
# Если такая обработка исключений не вызывает у вас восторга - измените код используя try except


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as err_t:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            logging.exception("%s - Возникло исключение с Telegram API!" % current_time)
            # print(err_t)
            time.sleep(20)
        except requests.exceptions.ReadTimeout:
            # обработка ошибок при получении данных с сервера
            count_err += 1
            print('Ошибка - Время ожидания ответа сервера Telegram истекло.')
            print("Всего ошибок %d шт." % count_err)
            time.sleep(20)
        except requests.exceptions.ConnectionError:
            # обработка ошибок при отсутствии связи
            pause = 120
            count_err += 1
            print('Ошибка - [WinError 10051] Сделана попытка выполнить операцию на сокете при отключенной сети.')
            print("Всего ошибок %d шт." % count_err)
            if count_err > 15:  # при наличи 15 ошибок сбрасываем счетчик и делаем паузу 1 час
                pause = 12000
                count_err = 0
                print("Обнаружено слишком много ошибок, спим %d сек." % pause)
            time.sleep(pause)
    # try:
    #     bot.infinity_polling(logger_level=logging.DEBUG, timeout=10, long_polling_timeout=5)
    # # ConnectionError и ReadTimeout из-за возможного таймаута библиотеки requests
    # except requests.exceptions.ReadTimeout:
    #     # обработка ошибок при получении данных с сервера
    #     count_err += 1
    #     print('Ошибка - Время ожидания ответа истекло.')
    #     print("Всего ошибок %d шт." % count_err)
    #     time.sleep(10)
