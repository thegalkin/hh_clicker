import pickle
import os
import time
import random
import sys
import urllib.parse
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException


BAN_LIST_FILE = 'ban_list.txt'
# Загрузка бан-листа из файла
def load_ban_list():
    if not os.path.exists(BAN_LIST_FILE):
        return []
    with open(BAN_LIST_FILE, 'r') as f:
        return [line.strip() for line in f]

# Сохранение бан-листа в файл
def save_ban_list(ban_list):
    with open(BAN_LIST_FILE, 'w') as f:
        for item in ban_list:
            f.write("%s\n" % item)

bad_test_vacancies = load_ban_list()

def get_vacancy_id_from_href(vacancy_href):
    parsed_href = urlparse(vacancy_href)
    query_params = parse_qs(parsed_href.query)
    vacancy_id = query_params.get('vacancyId', [''])[0]
    return vacancy_id

def check_and_fill_salary_form(browser, url, text_ot):
    save_ban_list(bad_test_vacancies)
    def submit_igoring_test():
        try:
            submit_without_doing_test = browser.find_element(By.XPATH, '//*[@id="RESPONSE_MODAL_FORM_ID"]/div[6]/div[2]/div/button')
            submit_without_doing_test.click()
        except:
            vacancy_id = ''
            try:
                vacancy_href = browser.find_element(By.XPATH, '//*[@id="HH-React-Root"]/div/div/div[4]/div[1]/div/div/div[1]/h3/a')[0].get_attribute('href')
                vacancy_id = get_vacancy_id_from_href(vacancy_href)
            except:
                vacancy_id = get_vacancy_id_from_href(browser.current_url)

            bad_test_vacancies.append(vacancy_id)
            browser.back()
            
    try:
        if len(browser.find_elements(By.XPATH, '//textarea[@data-qa="vacancy-response-popup-form-letter-input"]')) > 0 and len(browser.find_elements(By.XPATH, '//button[@data-qa="vacancy-response-submit-popup"]')) > 0:
                                textarea = browser.find_element(By.XPATH, '//textarea[@data-qa="vacancy-response-popup-form-letter-input"]')
                                button = browser.find_element(By.XPATH, '//button[@data-qa="vacancy-response-submit-popup"]')
                                textarea.send_keys(text_ot)
                                try:
                                    button.click()
                                except WebDriverException:
                                    pass
                                browser.get(url)
        else:
            submit_igoring_test()
    except:
        try:
            submit_igoring_test()
        except:
            pass
    


def run_try():
    # Определяем пути к драйверу и файлу cookies
    chrome_driver_path = '/usr/local/bin/chromedriver'  # путь к драйверу Chrome
    cookies_path = 'cookies.pkl'

    # Функция для сохранения cookies
    def save_cookies(driver, cookie_name):
        cookies = driver.get_cookies()
        with open(cookie_name, 'wb') as f:
            pickle.dump(cookies, f)

    # Функция для загрузки cookies
    def load_cookies(driver, cookie_name):
        try:
            with open(cookie_name, 'rb') as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        except FileNotFoundError:
            pass

    # Настройка браузера
    service = Service(executable_path=chrome_driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.page_load_strategy = 'eager'
    # Создаем экземпляр браузера
    browser = webdriver.Chrome(service=service, options=options)
    # browser.set_page_load_timeout(2)
    excluded_text = '1C,1С,Сбор и анализ требований бизнеса'
    base_url = f'https://hh.ru/search/vacancy?area=1&salary=260000&excluded_text={excluded_text}&employment=full&professional_role=148&text=системный+аналитик&schedule=remote&hhtmFrom=account_login&order_by=salary_desc'
    text_ot = 'Добрый день, мои зарплатные ожидания зависят от сложности проекта, но минимальная вилка - 300т.р. чистыми'
    page_param = '&page='
    num_pages = 30
    # Открываем сайт для загрузки cookies
    browser.get(base_url)
    load_cookies(browser, cookies_path)
    browser.get(base_url)  # Перезагружаем страницу после загрузки cookies

    # Ждем, пока пользователь войдет в систему вручную, если это первый запуск
    if "https://hh.ru/" == browser.current_url:
        input('Please login manually and press Enter to continue...')
        save_cookies(browser, cookies_path)

    # Ваши параметры поиска вакансий


    # Цикл по страницам для получения ссылок на вакансии
    for i in range(num_pages):
        if i == 0:
            url = base_url
        else:
            url = base_url + page_param + str(i+1)

        browser.get(url)
        break_flag = False
        while True:
            job_buttons = browser.find_elements(By.XPATH, '//a[@data-qa="vacancy-serp__vacancy_response"]')
            job_links = []
            for button in job_buttons:
                job_links.append(button.get_attribute('href'))
            try:
                if len(browser.find_element(By.XPATH, '/html/body/div[7]/div/div/div/div[2]/div[1]/div')) > 0:
                    print("Достигнут лимит по откликам. Запускайте скрипт через 24 часа.")
                    sys.exit(0)
            except:
                pass
            # if  len(job_links) == 0:
                # sys.exit(0)
            
            if break_flag:
                break

            else:
                for link in job_links:
                    browser.get(link)
                    time.sleep(random.randint(3, 5))
                    if link == job_links[len(job_links)-1]:
                        break_flag = True
            

    browser.quit()

while True:
    try:
        run_try()
    except Exception as e:
        print(e)
        pass