from datetime import datetime

from dateutil.relativedelta import relativedelta
from robocorp.tasks import task
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

link = 'https://www.reuters.com/'
search_term = 'brazil'
category = 'Market'
months = 2

@task
def execute_scraper():
    scraper = NewsScraper(link)
    scraper.open_site()
    scraper.search(search_term)
    scraper.category_filter(category)
    scraper.get_articles()


class NewsScraper:
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Chrome()  

    def open_site(self):
        self.driver.get(self.url)

    def search(self, search_word):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-bar__icon__ORXTq")))
        self.driver.find_element(By.CLASS_NAME, "search-bar__icon__ORXTq").click()
        input = self.driver.find_element(By.TAG_NAME, 'input')
        input.send_keys(search_word)
        input.send_keys(Keys.RETURN)

    def category_filter(self, category_search):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "sectionfilter")))
        dropdown = self.driver.find_element(By.XPATH,"//*[@id='sectionfilter' and self::button]")
        dropdown.send_keys(category_search)

    def get_articles(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-results__sectionContainer__34n_c")))
        news = self.driver.find_elements(By.XPATH, "//div[@class='search-results__sectionContainer__34n_c']//ul//li")
        current_dt = datetime.now()
        date_search = current_dt - relativedelta(months=5)
        date_search = date_search.replace(day=1) # get until the first date of specified month
        



