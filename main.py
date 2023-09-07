import requests
import bs4
import fake_headers
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
import re
from unicodedata import normalize
import json


def wait_element(browser, delay_seconds=1, by=By.TAG_NAME, value=None):
    return WebDriverWait(browser, delay_seconds).until(expected_conditions.presence_of_element_located((by, value)))
        
pattern = re.compile(r"(Django)|(Flask)", re.MULTILINE | re.IGNORECASE)
link = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
headers_fake = fake_headers.Headers(browser='chrome', os='win')

# Парсинг основного кода через selenium
chrome_driver_path = ChromeDriverManager().install()
browser_service = Service(executable_path=chrome_driver_path)
browser = Chrome(service=browser_service)
browser.get(link)
main_html = browser.page_source
#vacancy_serp_content_tag = wait_element(browser, by=By.CLASS_NAME, value='vacancy-serp-content')

#Парсинг основного кода через BS4. Делается для быстроты парсинга, не все вакансии берет
# response = requests.get(link, headers=headers_fake.generate())
# main_html = response.text

main_soup = bs4.BeautifulSoup(main_html, 'lxml')
vacancy_serp_content_tag = main_soup.find('main', class_ = 'vacancy-serp-content')
serp_item_tag = vacancy_serp_content_tag.find_all('div', class_='vacancy-serp-item-body__main-info')
vacancy_list = []
for vacancy in serp_item_tag:
    time.sleep(0.1)
    serp_item__title_tag = vacancy.find('a', class_='serp-item__title')
    title_vacancy = serp_item__title_tag.text
    link_vacancy = serp_item__title_tag['href']
    name_company = vacancy.find('div', class_='vacancy-serp-item__meta-info-company').text
    city = vacancy.find('div', {'data-qa':'vacancy-serp__vacancy-address'}).text
    time.sleep(0.1)
    response_vacancy = requests.get(link_vacancy, headers=headers_fake.generate())
    html_vacancy = response_vacancy.text
    vacancy_soup = bs4.BeautifulSoup(html_vacancy, 'lxml')
    #main_content_tag = html_vacancy.find('div', class_='main-content')
    text_vacancy = vacancy_soup.find('div', class_='g-user-content').text
    salary_tag = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
    if salary_tag is None:
        salary = 'Не указана'
    else:
        salary = salary_tag.text
    if pattern.search(text_vacancy) is None:
        next
    else:
        vacancy_list.append(
            {
                'title': normalize('NFKD', title_vacancy),
                'link' : normalize('NFKD', link_vacancy),
                'city' : normalize('NFKD', city),
                'salary' : normalize('NFKD', salary)
            } )
    print()
with open ('vacancy.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(vacancy_list, indent=2, ensure_ascii=False))
    print('Данные записаны в файл')