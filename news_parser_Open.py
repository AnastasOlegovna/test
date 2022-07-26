from bs4 import BeautifulSoup  # подключаем библиотеку для извлечения данных из файлов HTML и XML
import logging  # подключаем библиотеку логгинга
import time  # подключаем библиотеку для работы с временем
from selenium import webdriver  # подключаем библиотеку для работы с сайтами

base_file2 = '/home/anastasia/python/base2.txt'  # !!! пофиксить пути!!!

# создаем двумерный массив для сайтов [url_site][back_post_id]
site = [["https://www.facebook.com/silpo", 0],  # создано 24.07.2022
        ["https://www.facebook.com/sviymarket", 0],  # создано 25.07.2022
        ["https://www.facebook.com/varusua", 0],
        ["https://www.facebook.com/myasorubka.sumy", 0],
        ]  # создано 26.07.2022

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


def parser_all(url, back_post_title):
    # обнуляем переменные
    post = ""
    post_title = back_post_title
    page = get_page(url)  # получение страницы
    if page is None:
        return None, post_title

    try:
        soup = BeautifulSoup(page, "html.parser")
        if url == "https://www.facebook.com/silpo":  # функция для facebook silpo
            post = soup.find("div", class_='ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a')
            post_title = "*Сильпо:*" + post.find(style="text-align: start;").text


        elif url == "https://www.facebook.com/sviymarket":  # функция для сайта facebook свой маркет
            post = soup.find("div", class_='ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a')
            items = post.find_all(style='text-align: start;')
            post_common = []
            for item in items:
                post_common.append(item.get_text(strip=True))
            post_common.pop()
            post_common = " ".join(post_common)
            post_title = "*Свой маркет:*" + post_common

        elif url == "https://www.facebook.com/varusua":  # функция для сайта facebook varus
            post = soup.find("div", class_='ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a')
            items = post.find_all(style='text-align: start;')
            post_common = []
            for item in items:
                post_common.append(item.get_text(strip=True))
            post_common.pop()
            post_common = " ".join(post_common)
            post_title = "*Varus:*" + post_common

        elif url == "https://www.facebook.com/myasorubka.sumy":  # функция для сайта facebook mysorubka
            post = soup.find("div", class_='ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a')
            items = post.find_all(style='text-align: start;')
            post_common = []
            for item in items:
                post_common.append(item.get_text(strip=True))
            post_common.pop()
            post_common = " ".join(post_common)
            post_title = "*Myasorubka:*" + post_common

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

    if post_title != back_post_title:
        return f"{post_title}\n", post_title
    else:
        return None, post_title


def get_page(page_url):  # Общая функция получения страницы
    # выполняем запрос, в случае ошибки повторяем три раза
    page_ret = None
    n = 0
    while n <= 3:
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            driver = webdriver.Chrome(executable_path='/home/anastasia/python/chromedriver', chrome_options=options)
            driver.get(page_url)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(10)
            page_ret = driver.page_source
            driver.quit()
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
