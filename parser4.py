import logging
import collections
import csv
import bs4
import requests

'''
Парсер Wildberries(не работает)

Проблема скорее всего в функции parse_block
Не парсит элементы сайта, но в выводе появляются какие-то ссылки(по типу https://vsemrabota.ru/appwb/),
которые вообще не понятно откуда там берутся
'''
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')


ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'url',
    ),
)

HEADERS = (
    'Бренд',
    'Товар',
    'Ссылка',
)


class WBParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/113.0.0.0 Safari/537.36"
        }
        self.result = []

    def load_page(self):
        url = 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/bryuki-i-shorty'
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div', class_='product-card__wrapper')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):
        url_block = block.select_one('a', class_='product-card__link.j-card-link.j-open-full-product-card')
        if not url_block:
            logger.error('no url_block')
            return

        url = url_block.get('href')
        if not url:
            logger.error('no href')
            return

        name_block = block.select_one('h2', class_='product-card__brand-wrap')
        if not name_block:
            logger.error(f'no name_block on {url}')
            return

        brand_name = name_block.select_one('span', class_='product-card__brand')
        if not brand_name:
            logger.error(f'no brand_name on {url}')
            return

        goods_name = name_block.select_one('span', class_='product-card__name')
        if not goods_name:
            logger.error(f'no goods_name on {url}')
            return

        goods_name = goods_name.text.strip()

        self.result.append(ParseResult(
            url=url,
            brand_name=brand_name,
            goods_name=goods_name,
        ))

        logger.debug('%s, %s, %s', url, brand_name, goods_name)

    def save_result(self):
        with open(r"C:\Users\mastermor\Desktop\parse.csv", "w") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self):
        text = self.load_page()
        self.parse_page(text=text)
        logger.info(f'Получили {len(self.result)} элементов')
        #self.save_result()


if __name__ == '__main__':
    parser4 = WBParser()
    parser4.run()
