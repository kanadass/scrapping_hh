import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json


url = f'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
ua = UserAgent()
headers = {"user-agent": ua.random}
params = {
    "text": "python",
    "area": [1, 2]
}

def get_vacancies():
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        all_vacancies = soup.find_all('div', class_='vacancy-serp-item-body__main-info')
        vacancies = []
        for vacancy in all_vacancies:
            vacancies.append(vacancy)
    return vacancies

def get_data(vacancies):
    data = []
    for vacancy in vacancies:
        title = vacancy.find('a', class_='serp-item__title').text
        company = vacancy.find_next('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).text
        salary = vacancy.find_next('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        salary = salary.text if salary else 'unspecified'
        city = vacancy.find('div', class_='bloko-text', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
        link = vacancy.find('a', {'data-qa': 'serp-item__title'}).get('href')

        if link:
            response = requests.get(link, headers=headers, params=params)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                vacancy_tags = soup.find('div', class_='bloko-tag-list')
                vacancy_tags = vacancy_tags.find_all("span") if vacancy_tags else []

                tags = []
                for tag in vacancy_tags:
                    tags.append(tag.text.lower())
        data.append(
            {
                'title': title,
                'link': link,
                'company': company.replace(' ', ' '),
                'city': city,
                'salary': salary.replace(' ', ''),
                'tags': tags,
            }
        )
    return data

def filter_django_flask(data):
    res = []
    for dct in data:
        if 'flask' in dct['tags'] or 'django' in dct['tags']:
            res.append(dct)
    return res

def write_to_json(data):
    with open('vacancies.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f'The data has been successfully written to JSON')

if __name__ == '__main__':
    vacancies = get_vacancies()
    data = get_data(vacancies)
    filtered_data = filter_django_flask(data)
    write_to_json(filtered_data)
