# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы
# получаем должность) с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать
# несколько страниц сайта (также вводим через input или аргументы). Получившийся список должен содержать
# в себе минимум:
# Наименование вакансии.
# Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
# Ссылку на саму вакансию.
# Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
# Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью
# dataFrame через pandas. Сохраните в json либо csv.

from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd

RESULT_FILE_PATH_CSV = 'vacancies.csv'


def calc_salary(vacancy, tag, param, value):
    """
    Возвращает минимальную и максимальную границы зарплаты по вакансии
    :param vacancy:
    :param tag:
    :param param:
    :param value:
    :return:
    """
    try:
        vacancy_salary = vacancy.find(tag, {param: value}).text
        salary = [el.replace('\xa0', '') for el in re.findall(r'\d+\s\d+', vacancy_salary)]
        currency = vacancy_salary.split()[-1]
        if vacancy_salary != 'По договорённости':
            if vacancy_salary.startswith('от'):
                salary_min = salary[0]
                salary_max = ''
            elif vacancy_salary.startswith('до'):
                salary_min = ''
                salary_max = salary[0]
            elif len(salary) == 2:
                salary_min = salary[0]
                salary_max = salary[1]
            else:
                salary_min = salary_max = salary[0]
        else:
            salary_min = ''
            salary_max = ''
    except:
        salary_min = ''
        salary_max = ''
        currency = ''
    return salary_min, salary_max, currency


def scan_hh():
    """
    Возвращает DataFrame с вакансиями hh.ru
    :return:
    """
    page = 0
    vacancies = []
    while True:
        print(f'Сканируем hh.ru - стр. {page}', end='')
        main_link = 'https://hh.ru'
        params = {'L_is_autosearch': 'false',
                  'area': '1',
                  'clusters': 'true',
                  'enable_snippets': 'true',
                  'search_field': 'name',
                  'text': user_request,
                  'page': str(page)}

        html = requests.get(main_link + '/search/vacancy', params=params, headers=headers)

        soup = bs(html.text, 'html.parser')

        vacancies_block = soup.find('div', {'class': 'vacancy-serp'})
        vacancies_list = vacancies_block.find_all('div', {'class': 'vacancy-serp-item'})

        for vacancy in vacancies_list:
            vacancy_data = {}
            vacancy_name = vacancy.find('a').text      # Наименование вакансии
            vacancy_link = vacancy.find('a')['href']   # Ссылка на вакансию
            # Зарплата
            salary_min, salary_max, currency = calc_salary(vacancy, 'span', 'data-qa', 'vacancy-serp__vacancy-compensation')

            # Работодатель
            try:
                vacancy_employer = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).text.strip()
            except:
                vacancy_employer = ''
            # Запихиваем значения в словарь
            vacancy_data['name'] = vacancy_name
            vacancy_data['link'] = vacancy_link
            vacancy_data['min_salary'] = salary_min
            vacancy_data['max_salary'] = salary_max
            vacancy_data['currency'] = currency
            vacancy_data['employer'] = vacancy_employer
            vacancy_data['source'] = 'hh.ru'
            # Добавляем в список вакансий
            vacancies.append(vacancy_data)
        if soup.find('a', {'data-qa': 'pager-next'}):
            page += 1
            print('', end='\r')
        else:
            break
    print(f'\nНайдено {len(vacancies)} вакансий.')
    result = pd.DataFrame(vacancies)
    return result


def scan_superjob():
    """
        Возвращает DataFrame с вакансиями superjob.ru
        :return:
    """
    vacancies = []
    page = 0
    while True:
        print(f'Сканируем superjob.ru - стр. {page}', end='')
        main_link = 'https://www.superjob.ru'
        params = {'keywords': user_request,
                  'geo[t][0]': '4',
                  'page': f'{page}'
                  }

        html = requests.get(main_link + '/vacancy/search/', params=params, headers=headers)
        soup = bs(html.text, 'html.parser')
        try:
            vacancies_block = soup.find_all('div', {'class': '_3zucV undefined _3SGgo'})[2]
            vacancies_list = vacancies_block.find_all('div', {'class': '_3zucV _1fMKr undefined _3tcTB _3SGgo'})
            for vacancy in vacancies_list:
                vacancy_data = {}
                if vacancy.find('div', {'class': 'iJCa5 f-test-vacancy-item _1fma_ undefined _2nteL'}):
                    vacancy_name = vacancy.find('a').text                   # Наименование вакансии
                    vacancy_link = main_link + vacancy.find('a')['href']    # Ссылка на вакансию
                    # Зарплата
                    salary_min, salary_max, currency = calc_salary(vacancy, 'span', 'class',
                                                         '_1OuF_ _1qw9T f-test-text-company-item-salary')
                    # Работодатель
                    vacancy_employer = vacancy.find('span', {'class': '_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc _2VHxz _15msI'}).text
                    # Запихиваем значения в словарь
                    vacancy_data['name'] = vacancy_name
                    vacancy_data['link'] = vacancy_link
                    vacancy_data['min_salary'] = salary_min
                    vacancy_data['max_salary'] = salary_max
                    vacancy_data['currency'] = currency
                    vacancy_data['employer'] = vacancy_employer
                    vacancy_data['source'] = 'superjob.ru'
                    # Добавляем в список вакансий
                    vacancies.append(vacancy_data)
            if soup.find('a', {'class': 'icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-Dalshe'}):
                page += 1
                print('', end='\r')
            else:
                break
        except:
            print('\nВакансий не найдено.')
            return
    print(f'\n Найдено {len(vacancies)} вакансий.')
    result = pd.DataFrame(vacancies)
    return result

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 YaBrowser/21.8.1.476 Yowser/2.5 Safari/537.36'}

user_request = input('Укажите название вакансии: ')

vacancies_table = pd.DataFrame(columns=['name', 'link', 'min_salary', 'max_salary', 'currency', 'employer', 'source'])
vacancies_table = pd.concat([vacancies_table, scan_hh(), scan_superjob()])
print(f'\nИтого найдено {vacancies_table.shape[0]} вакансий.')
vacancies_table.to_csv(RESULT_FILE_PATH_CSV, index=False, encoding='utf-8')
print(f'Результаты сохранены в файл {RESULT_FILE_PATH_CSV}')