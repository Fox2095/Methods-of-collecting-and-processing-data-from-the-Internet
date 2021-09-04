# 2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему,
# пройдя авторизацию. Ответ сервера записать в файл.
# Если нет желания заморачиваться с поиском, возьмите API вконтакте (https://vk.com/dev/first_guide).
# Сделайте запрос, чтобы получить список всех сообществ на которые вы подписаны.

import requests
import json

user_id ='123456'
access_token = '213464641136fgcgcf'
url = f'https://api.vk.com/method/groups.get?user_id{user_id}&access_token{access_token}&v=5.52'
group_data_base=[]
req = requests.get(url)
group_data = req['response']['items']

for el in group_data:
    group_data_base.append(f'{el["id"]} - {el["name"]}')


with open('json_hw1.2.json', 'w', encoding='ulf-8') as f:
    json.dump(group_data_base, f, sort_keys=True, indent=4, ensure_ascii=False)


