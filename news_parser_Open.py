from bs4 import BeautifulSoup  # подключаем библиотеку для извлечения данных из файлов HTML и XML
import requests  # подключаем HTTP библиотеку для работы с сайтами
import logging  # подключаем библиотеку логгинга
import time  # подключаем библиотеку для работы с временем
from selenium import webdriver

base_file2 = '/Users/User/base2.txt'  # !!! пофиксить пути!!!

# создаем двумерный массив для сайтов [url_site][back_post_id]
site = [["https://www.facebook.com/silpo", 0]]  # создано 20.07.2022


count = len(site)  # получаем количество строк в массиве
# работа с файлом хранения последних ИД статей по сайтам

try:
    file = open(base_file2, 'r')  # открываем файл для чтения
    # считываем все содержимое файла в одну строку, преобразуем в список удалением символов перевода строк
    param = file.read().splitlines()
    file.close()  # закрываем файл
except FileNotFoundError:
    print('Файл не існує!')
    my_file = open(base_file2, "w+")  # параметр "w+" сообщает, что запись будет осуществляться в новый файл.
    # Если он существует, то новое содержимое нужно записать поверх уже существующего.
    # параметр "w", тогда файл будет создан только в том случае, если он не существовал до этого.
    my_file.close()

    if len(param) == 0:
        print("Бот запущено! Файл порожній, ІД постів обнулені")
    elif len(param) == count:
        print("Бот запущено! Прочитані рядки файлу та отримані такі стартові значення:")
        for num in range(count):  #
            site[num][1] = param[num]  # переносим ИД
            print(site[num])


def get_post(index):
    post = parser_all(site[index][0], site[index][1])  # парсим сайт, отправляя его адрес и ИД предыдущего поста
    site[index][1] = post[1]  # сохраняем ИД текущего поста для следующего обращения
    return post


def parser_all(url, back_post_id):
    # обнуляем переменные
    post = ""
    post_title = ""
    post_url = ""
    post_id = back_post_id
    page = get_page(url)  # получение страницы
    if page is None:
        return None, post_id

    try:
        soup = BeautifulSoup(page.content, "html.parser")
        if url == "https://www.facebook.com/silpo":  # функция для facebook silpo
            post = soup.find("div", class_='ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a')
            post_title = post.find(style="text-align: start;").text
            post_id = post.title


        # elif url == "https://forbes.ua/news":  # функция для сайта forbes.ua
        #     post = soup.find("div", class_="c-feed-col").find("h3", class_="c-entry-title")
        #     post_id_url = post.find("a", href=True)['href'].strip()
        #     # разделяем строку по "-", берем последний элемент получившегося списка
        #     post_id = post_id_url.split('-')[-1]
        #     # post_id = post_id_url[-4:-0]


        else:
            print("Вказана адреса сайту не знайдена для вибору обробника %s" % url)

    except KeyError:
        print("Помилка ключа для сайту %s" % url)
    except (AttributeError, TypeError) as e:
        print("Отримано помилку при парсингу або розборі сторінки сайту %s: " % url)
        print(e)
        if post is not None:
            file_w = open('soup_err.txt', 'w')
            file_w.write(post)
            file_w.close()

    if post_id != back_post_id:
        return f"{post_title}\n\n{post_url}", post_id
    else:
        return None, post_id


def get_page(page_url):  # Общая функция получения страницы
    # выполняем запрос, в случае ошибки повторяем три раза
    headers = {'User-Agent': 'Mozilla/5.0'}
    page_ret = None
    n = 0
    while n <= 3:
        try:
            driver = webdriver.Chrome(executable_path='C:\\Users\\User\\chromedriver.exe')
            driver.get(page_url)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(10)
            page_ret = driver.page_source
        # except requests.exceptions:    # except requests.exceptions.ConnectionError:
        except Exception as erro:
            # r.status_code = "Connection refused"
            current_time = time.strftime("%H:%M:%S", time.localtime())
            # print("%s - Ошибка связи, повторяем" % current_time)
            # print(ex)
            logging.exception("%s - Виникло виключення!" % current_time)
            print(erro)
            time.sleep(20)  # задержка перед повторным запросом
            n += 1
            # page_ret = requests.get(page_url)
        else:
            return page_ret
    return page_ret
    # else выполняется в том случае, если исключения не было, а finally в любом
