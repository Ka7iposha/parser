from bs4 import BeautifulSoup
import requests
'''
Простой парсер авито

Парсит только ссылки на товары, на одной странице
'''
product = input()

url = "https://www.avito.ru/vologda?q=" + product
request = requests.get(url)
bs = BeautifulSoup(request.text, "html.parser")

all_links = bs.find_all("a", class_="iva-item-title-py3i_")

output_file = open(r"C:\Users\mastermor\Desktop\parser.txt", "w", encoding='utf-8')
for link in all_links:
    print("https://www.avito.ru" + link["href"], file=output_file)
output_file.close()
