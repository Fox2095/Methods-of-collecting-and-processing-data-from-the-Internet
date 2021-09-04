# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного
# пользователя, сохранить JSON-вывод в файле *.json.

import requests
import json

url = 'https://api.github.com'
user='Fox2095'

r = requests.get(f'{url}/users/{user}/repos')

with open('json_hw1.1.json', 'w') as f:
    json.dump(r.json(), f)

for i in r.json():
    print(i['name'])