import requests
import logging
import os
import csv

'''

Парсер wb через API

'''
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')


def get_catalogs_wb():
    """получение каталога вб"""
    url = 'https://static-basket-01.wb.ru/vol0/data/main-menu-ru-ru-v2.json'
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    data = response.json()
    data_list = []
    for d in data:
        try:
            for child in d['childs']:
                try:
                    category_name = child['name']
                    category_url = child['url']
                    shard = child['shard']
                    query = child['query']
                    data_list.append({
                        'category_name': category_name,
                        'category_url': category_url,
                        'shard': shard,
                        'query': query})
                except:
                    continue
                try:
                    for sub_child in child['childs']:
                        category_name = sub_child['name']
                        category_url = sub_child['url']
                        shard = sub_child['shard']
                        query = sub_child['query']
                        data_list.append({
                            'category_name': category_name,
                            'category_url': category_url,
                            'shard': shard,
                            'query': query})
                except:
                    logger.debug(f'не имеет дочерних каталогов *{i["name"]}*')
                    continue
        except:
            logger.debug(f'не имеет дочерних каталогов *{d["name"]}*')
            continue
    return data_list


def search_category_in_catalog(url, catalog_list):
    """пишем проверку пользовательской ссылки на наличии в каталоге"""
    try:
        for catalog in catalog_list:
            if catalog['category_url'] == url.split('https://www.wildberries.ru')[-1]:
                logger.info(f'найдено совпадение: {catalog["category_name"]}')
                name_category = catalog['category_name']
                shard = catalog['shard']
                query = catalog['query']
                return name_category, shard, query
            else:
                # print('нет совпадения')
                pass
    except:
        logger.info('Данный раздел не найден!')


def get_data_from_json(json_file):
    """извлекаем из json интересующие нас данные"""
    data_list = []
    for data in json_file['data']['products']:
        try:
            price = int(data["priceU"] / 100)
        except:
            price = 0
        data_list.append({
            'Наименование': data['name'],
            'id': data['id'],
            'Скидка': data['sale'],
            'Цена': price,
            'Цена со скидкой': int(data["salePriceU"] / 100),
            'Бренд': data['brand'],
            'id бренда': int(data['brandId']),
            'feedbacks': data['feedbacks'],
            'rating': data['rating'],
            'Ссылка': f'https://www.wildberries.ru/catalog/{data["id"]}/detail.aspx?targetUrl=BP'
        })
    return data_list


def get_content(output_file, shard, query, low_price=None, top_price=None):
    # вставляем ценовые рамки для уменьшения выдачи, вайлдберис отдает только 100 страниц
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    data_list = []
    with open(f'{output_file}', "w", encoding='utf16', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=';')
        writer.writerow(['title', 'price', 'currency', 'url'])
        for page in range(1, 101):
            logger.info(f'Сбор позиций со страницы {page} из 100')
            url = f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&curr=rub&dest=-1075831,-77677,-398551,12358499' \
                  f'&locale=ru&page={page}&priceU={low_price * 100};{top_price * 100}' \
                  f'&reg=0&regions=64,83,4,38,80,33,70,82,86,30,69,1,48,22,66,31,40&sort=popular&spp=0&{query}'
            r = requests.get(url, headers=headers)
            data = r.json()
            logger.info(f'Добавлено позиций: {len(get_data_from_json(data))}')
            if len(get_data_from_json(data)) > 0:
                data_list.extend(get_data_from_json(data))
            else:
                logger.info(f'Сбор данных завершен.')
                break
            writer.writerow(data_list)
    return data_list


#def save_excel(data):
  #  """сохранение результата в excel файл"""
 #   with open(r"C:\Users\mastermor\Desktop\parser.txt", 'a', encoding='UTF-8') as file:
   #     file.write(data)



def parser(url, low_price, top_price):
    # получаем список каталогов
    catalog_list = get_catalogs_wb()
    try:
        # поиск введенной категории в общем каталоге
        name_category, shard, query = search_category_in_catalog(url=url, catalog_list=catalog_list)
        # сбор данных в найденном каталоге
        xlsx_path = os.path.dirname(__file__) + r'\parserr.csv'
        data_list = get_content(xlsx_path, shard=shard, query=query, low_price=low_price, top_price=top_price)
        # сохранение найденных данных
        # save_excel(data_list)
    except TypeError:
        logger.info('Ошибка! Возможно не верно указан раздел. Удалите все доп фильтры с ссылки')
    except PermissionError:
        logger.info('Ошибка! Вы забыли закрыть созданный ранее excel файл. Закройте и повторите попытку')


if __name__ == '__main__':
    """ссылку на каталог или подкаталог, указывать без фильтров (без ценовых, сортировки и тд.)"""
    # url = input('Введите ссылку на категорию для сбора: ')
    # low_price = int(input('Введите минимальную сумму товара: '))
    # top_price = int(input('Введите максимульную сумму товара: '))

    """данные для теста. собераем товар с раздела велосипеды в ценовой категории от 50тыс, до 100тыс"""
    url = 'https://www.wildberries.ru/catalog/sport/vidy-sporta/velosport/velosipedy'
    # url = 'https://www.wildberries.ru/catalog/elektronika/noutbuki-pereferiya/periferiynye-ustroystva/mfu'
    # url = 'https://www.wildberries.ru/catalog/dlya-doma/predmety-interera/dekorativnye-nakleyki'
    low_price = 5000
    top_price = 100000

    parser(url, low_price, top_price)
