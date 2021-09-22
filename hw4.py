# Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# Сложить собранные данные в БД
# Минимум один сайт, максимум - все три

from pprint import pprint
from lxml import html
import requests
import re
from pymongo import MongoClient

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}
client = MongoClient('127.0.0.1', 27017)
db = client['news']


def lenta_scan():
    """
    Собирает новости с сайта lenta.ru
    :return:
    """
    main_link = 'https://lenta.ru'
    response = requests.get(main_link, headers=header)
    dom = html.fromstring(response.text)
    pprint('Сканируем lenta.ru')
    news_list = []
    news_block = dom.xpath("//section[@class='row b-top7-for-main js-top-seven']//div[contains(@class, 'item')]")
    for item in news_block:
        news = {}
        subject = item.xpath(".//a/text()")[0]
        link = item.xpath(".//a/@href")[0]
        if not link.startswith('http'):
            date = '/'.join(re.findall(r'\d\d\d\d\D\d\d\D\d\d', link)[0].split('/')[::-1])
            news['source'] = 'lenta.ru'
            news['link'] = main_link + link
        else:
            date = re.findall(r'\d\d\D\d\d\D\d\d\d\d', link)[0]
            news['source'] = 'lenta.ru'
            news['link'] = link
        news['subject'] = subject

        news['date'] = date
        news_list.append(news)

    pprint(f'Собрано {len(news_list)} новостей')

    return news_list

def add_to_db(source, news_list):
    """
    Добавляет новости в базу, если таких еще нет.
    :param source: сканируемый ресурс, используется в качестве имени коллекции
    :param news_list: список новостей
    :return:
    """
    counter = 0
    for news in news_list:
        if db[source].count_documents({'subject': news['subject']}) == 0:
            db[source].insert_one(news)
            counter += 1
    pprint(f'В базу добавлено {counter} новостей.')

add_to_db('lenta', lenta_scan())