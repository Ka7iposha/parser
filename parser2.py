import random
import re
import time
import pandas
import requests
from bs4 import BeautifulSoup
from pandas import ExcelWriter


def get_html(url, params=None):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0)"
    }
    proxies = {
        'https': 'http://95.79.53.19:8080'
    }
    html = requests.get(url, headers=headers, proxies=proxies, params=params)
    return html


def get_pages(html):
    soup = BeautifulSoup(html.text, "lxml")
    try:
        pages = soup.find('span', {'data-marker': 'pagination-button/nextPage'}).previous_element
    except:
        pages = 1
    print('Количество найденных страниц: ', pages)
    return pages


def get_content(html):
    soup = BeautifulSoup(html.text, 'html.parser')
    blocks = soup.find_all('div', class_=re.compile('iva-item-content'))
    data=[]
    for block in blocks:
        name = block.find('h3', class_=re.compile('title-root')).get_text(strip=True)
        price = block.find('span', class_=re.compile('price-text')).get_text(strip=True).replace('₽', '').replace('\xa0', '')
        city = block.find('a', class_=re.compile('link-link')).get('href').split('/')[1]
        district = block.find('div', class_=re.compile('geo-root')).get_text(strip=True)
        link = 'https://www.avito.ru/' + block.find('a', class_=re.compile('link-link')).get('href')
        with open(r"C:\Users\mastermor\Desktop\parser.txt", 'a', encoding='UTF-8') as file:
            file.write(f'{name} | {price} | {city} | {district} | {link}\n')
    return data


def parse(url):
    search = input('Введите запрос поиска: ')
    html = get_html(url, params={'bt': 1, 'q': search, 's': '2', 'view': 'gallery'})
    soup = BeautifulSoup(html.text, 'html.parser')
    print(soup.h1.get_text())
    print('Ссылка со всеми параметрами:\n', html.url)
    print('Статус код сайта: ', html.status_code)
    data=[]
    if html.status_code == 200:
        get_pages(html)
        pagination = int(input('Сколько страниц спарсить?'))
        for page in range(1, pagination + 1):
            html = get_html(url, params={'bt': 1, 'p': page,'q': search, 's': '2', 'view': 'gallery'})
            print(f'Парсинг страницы {page} из {pagination}...')
            data.extend((get_content(html)))
            time.sleep(random.randint(1, 3))
        print(f'Получили {len(data)} позиций')
    else:
        print('Ошибка доступа к сайту')


if __name__ == '__main__':
    parse('https://www.avito.ru/')
