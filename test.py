import requests
proxies = {
    'https': 'http://95.79.53.19:8080'
}

data = requests.get('https://ipinfo.io/json', proxies=proxies)
print(data.text)