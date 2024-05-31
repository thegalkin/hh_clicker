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
from selenium.common.exceptions import WebDriverException, NoSuchElementException, StaleElementReferenceException

# Файл для хранения бан-листа
BAN_LIST_FILE = 'ban_list.txt'
# Файл для хранения куки
COOKIES_FILE = 'cookies.pkl'

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

# Инициализация бан-листа
bad_test_vacancies = load_ban_list()

def get_vacancy_id_from_href(vacancy_href):
    parsed_href = urlparse(vacancy_href)
    query_params = parse_qs(parsed_href.query)
    vacancy_id = query_params.get('vacancyId', [''])[0]
    return vacancy_id

def check_and_fill_salary_form(browser, url, text_ot):
    def submit_igoring_test():
        try:
            submit_without_doing_test = browser.find_element(By.XPATH, '//*[@id="RESPONSE_MODAL_FORM_ID"]/div[6]/div[2]/div/button')
            submit_without_doing_test.click()
        except (NoSuchElementException, StaleElementReferenceException):
            vacancy_href = browser.find_elements(By.XPATH, '//*[@id="HH-React-Root"]/div/div/div[4]/div[1]/div/div/div[1]/h3/a')[0].get_attribute('href')
            vacancy_id = get_vacancy_id_from_href(vacancy_href)
            if vacancy_id not in bad_test_vacancies:
                try:
                    vacancy_name = browser.find_element(By.XPATH, '//*[@id="a11y-main-content"]/div[2]/div/div/h2/span/a/span').text
                    vacancy_salary = browser.find_element(By.XPATH, '//*[@id="a11y-main-content"]/div[2]/div/div/div[4]/div/span[1]/span').text
                    vacancy_company = browser.find_element(By.XPATH, '//*[@id="a11y-main-content"]/div[2]/div/div/div[6]/span[1]/span/a/span').text
                    note = f"{vacancy_id},{vacancy_name},{vacancy_company},{vacancy_salary}"
                    bad_test_vacancies.append(note)
                    save_ban_list(bad_test_vacancies)
                except:
                    pass
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
    except (NoSuchElementException, StaleElementReferenceException):
        try:
            submit_igoring_test()
        except (NoSuchElementException, StaleElementReferenceException):
            pass

def run_try():
    chrome_driver_path = '/usr/local/bin/chromedriver'  # путь к драйверу Chrome

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
                if "domain" in cookie and "hh.ru" in cookie["domain"]:
                    driver.add_cookie(cookie)
        except FileNotFoundError:
            pass

    # Настройка браузера
    service = Service(executable_path=chrome_driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.page_load_strategy = 'eager'
    browser = webdriver.Chrome(service=service, options=options)
    
    excluded_text = '1C,1С,Сбор и анализ требований бизнеса'
    base_url = f'https://hh.ru/search/vacancy?area=1&salary=260000&excluded_text={excluded_text}&employment=full&professional_role=148&text=системный+аналитик&schedule=remote&hhtmFrom=account_login'
    text_ot = 'Добрый день, мои зарплатные ожидания зависят от сложности проекта, но минимальная вилка - 300т.р. чистыми'
    page_param = '&page='
    num_pages = 30
    browser.get('https://hh.ru')
    # Загружаем cookies перед открытием страницы
    load_cookies(browser, COOKIES_FILE)
    browser.get(base_url)

    if "https://hh.ru/" == browser.current_url:
        input('Please login manually and press Enter to continue...')
        save_cookies(browser, COOKIES_FILE)

    for i in range(num_pages):
        if i == 0:
            url = base_url
        else:
            url = base_url + page_param + str(i + 1)

        browser.get(url)

        while True:
            job_links = browser.find_elements(By.XPATH, '//a[@data-qa="vacancy-serp__vacancy_response"]')
            if len(job_links) == 0:
                print("No more job links found.")
                break  # Выходим из while True, если нет ссылок на вакансии

            try:
                limit_reached = browser.find_elements(By.XPATH, '/html/body/div[7]/div/div/div/div[2]/div[1]/div')
                if len(limit_reached) > 0:
                    print("Достигнут лимит по откликам. Запускайте скрипт через 24 часа.")
                    sys.exit(0)
            except NoSuchElementException:
                pass

            for link in job_links:
                vacancy_id = get_vacancy_id_from_href(link.get_attribute('href'))
                if any(vacancy_id in item for item in bad_test_vacancies):
                    continue

                try:
                    link.send_keys(Keys.CONTROL + Keys.RETURN)
                    time.sleep(1)  # Ожидание для загрузки новой вкладки
                    browser.switch_to.window(browser.window_handles[-1])  # Переключаемся на новую вкладку

                    vacancy_name = browser.find_element(By.XPATH, '//*[@id="a11y-main-content"]/div[2]/div/div/h2/span/a/span').text
                    vacancy_salary = browser.find_element(By.XPATH, '//*[@id="a11y-main-content"]/div[2]/div/div/div[4]/div/span[1]/span').text
                    vacancy_company = browser.find_element(By.XPATH, '//*[@id="a11y-main-content"]/div[2]/div/div/div[6]/span[1]/span/a/span').text
                    print(f"Нажал откликнуться - {vacancy_name} {vacancy_company} {vacancy_salary}")
                    time.sleep(random.randint(3, 5))
                    if url != browser.current_url:
                        check_and_fill_salary_form(browser, url, text_ot)
                    browser.close()  # Закрываем вкладку
                    browser.switch_to.window(browser.window_handles[0])  # Возвращаемся на основную вкладку
                    save_ban_list(bad_test_vacancies)  # Сохраняем бан-лист после каждой итерации
                except (NoSuchElementException, StaleElementReferenceException):
                    pass
            break  # Выходим из while True после обработки всех ссылок

    browser.quit()

while True:
    try:
        run_try()
    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(10)  # добавляем задержку перед повторным запуском
