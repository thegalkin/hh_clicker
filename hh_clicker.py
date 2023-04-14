import time
import random
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.edge import service
from selenium.common.exceptions import NoSuchWindowException, NoSuchElementException, UnexpectedAlertPresentException


# Set up the browser
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome('./chromedriver', options=options)   # ubuntu
# browser = webdriver.Chrome('chromedriver', options=options)     # macos

# Python
exclude = 'senior,SQL,c++,devops,erlang,angular,php,sharepoint,react,react.JS,,vue,Vue.JS,typescript,Rust,golang,go,java,javascript,vba,node.js,delphi'
base_url = f'https://hh.ru/search/vacancy?area=113&excluded_text={exclude}&text=Python&schedule=remote&hhtmFrom=account_login'
text_ot = 'Привет!'

# Define the page parameter
page_param = '&page='

# Set the number of pages to navigate to
num_pages = 100

# Loop over each page and extract the job links
for i in range(num_pages):
    # Construct the URL for the current page
    if i == 0:
        url = base_url
    else:
        url = base_url + page_param + str(i+1)

    browser.get(url)

    # Wait for the user to login manually
    input(' Please login manually and press Enter to continue...')

    # Click on all buttons with the specified class name
    while True:
        
        job_links = browser.find_elements(By.XPATH, '//a[@data-qa="vacancy-serp__vacancy_response"]')
        
        if len(job_links) == 0:
            # No more job links on this page, break out of the loop
            break

        else:
            for link in job_links:
                # Open the button in the same tab
                try:
                    link.send_keys(Keys.CONTROL + Keys.RETURN)
                    # Wait for a random time between 2 and 9 seconds
                    sleep_time = random.randint(3,5)
                    time.sleep(sleep_time)
                    # Check if the popup with textarea and button appears
                    if len(browser.find_elements(By.XPATH, '//textarea[@data-qa="vacancy-response-popup-form-letter-input"]')) > 0 and len(browser.find_elements(By.XPATH, '//button[@data-qa="vacancy-response-submit-popup"]')) > 0:
                    # Find the textarea and button elements
                        textarea = browser.find_element(By.XPATH, '//textarea[@data-qa="vacancy-response-popup-form-letter-input"]')
                        button = browser.find_element(By.XPATH, '//button[@data-qa="vacancy-response-submit-popup"]')
                        # Print text in the textarea and click the button
                        textarea.send_keys(text_ot)
                        button.click()
                except:
                    pass

        # Check if the URL of the current page is different from the expected URL
        if url != browser.current_url:
            print(' Shit happened')
            print(' Issue page found. Paused until you return to the good URL.')
            print(' When you are back on the good URL, ')
            input(' -> hit any key to proceed...')
            pass
