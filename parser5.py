import requests
import json
import pandas as pd
import logging


'''
Парсер wb через API

Пока просто берутся данные из json файла на сайте
'''
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')

def get_catalogs_wb():
    """получение каталога вб"""
    url = 'https://static-basket-01.wb.ru/vol0/data/main-menu-ru-ru-v2.json'
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    data = response.json()
    with open(r"C:\Users\mastermor\Desktop\parser5.json", 'w', encoding='UTF-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        logger.info(f'Данные сохранены в parser5.json')
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


if __name__ == '__main__':
    get_catalogs_wb()