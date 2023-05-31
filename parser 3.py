from collections import namedtuple
import bs4
import requests
import csv

'''
Наиболее близкая к совершенству версия парсера авито

Также нет функции определяющей количестов страниц, которые нужно спарсить, но
можно указать в самой программе количесво этих страниц

Вывод записывается в csv файл
'''

InnerBlock = namedtuple('Block', 'title,price,currency,url')


class Block(InnerBlock):
    def __str__(self):
        return f'{self.title}\t{self.price} {self.currency}\t{self.url}'


class AvitoParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0)"
        }
        self.session.proxies = {
            'https': 'http://95.79.53.19:8080'
        }

    def get_page(self, page: int = None):
        params = {
        }
        if page and page > 1:
            params['p'] = page
        url = 'https://www.avito.ru/all/bytovaya_elektronika?q=Apple'
        r = self.session.get(url, params=params)
        print(r.status_code)
        return r.text

    def parse_block(self, item):
        url_block = item.select_one('a', class_='styles-module-root-QmppR styles-module-root_noVisited-aFA10')
        href = url_block.get('href')
        if href:
            url = 'https://www.avito.ru' + href
        else:
            url = None

        title_block = item.select_one('h3', class_='styles-module-root-TWVKW styles-module-root-_KFFt '
                                                   'styles-module-size_l-_oGDF styles-module-size_l-hruVE '
                                                   'styles-module-ellipsis-LKWy3 styles-module-weight_bold-Kpd5F '
                                                   'stylesMarningNormal-module-root-OSCNq '
                                                   'stylesMarningNormal-module-header-l-qvNIS')
        title = title_block.string.strip()

        price_block = item.select_one('p', {'data-marker': 'item-price'})
        price_block = price_block.get_text('\n')
        price_block = list(filter(None, map(lambda i: i.strip(), price_block.split('\n'))))
        if len(price_block) == 2:
            price, currency = price_block
        else:
            price, currency = None, None
            print('Что-то пошло не так при поиске цены:', price_block)

        return Block(
            url=url,
            title=title,
            price=price,
            currency=currency,
        )

    def get_blocks(self, page: int = None):
        text = self.get_page(page=page)
        soup = bs4.BeautifulSoup(text, 'lxml')

        container = soup.select('div.iva-item-content-rejJg')
        with open(r"C:\Users\mastermor\Desktop\parse.csv", "w", encoding='utf8', newline='') as output_file:
            writer = csv.writer(output_file, delimiter=';')
            writer.writerow(['title', 'price', 'currency', 'url'])
            for item in container:
                block = self.parse_block(item=item)
                writer.writerow(block)

    def parse_all(self):
        limit = 4
        print(f'Всего страниц: {limit}')
        for i in range(1, limit + 1):
            self.get_blocks(page=i)


def main():
    p = AvitoParser()
    # p.parse_all()
    p.get_blocks()


if __name__ == '__main__':
    main()
