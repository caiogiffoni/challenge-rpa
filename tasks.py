import re
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta
from robocorp.tasks import task
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# link = 'https://www.reuters.com/'
link = 'https://www.reuters.com/site-search/?query=brazil&section=markets'
search_term = 'brazil'
category = 'Market'
months = 5
columns = ['title', 'date', 'pic_filename', 'count_phases', 'money_in_title']

@task
def execute_scraper():
    scraper = NewsScraper(link)
    scraper.open_site()
    # scraper.search(search_term)
    # scraper.category_filter(category)
    items = scraper.get_articles(search_term, months)
    scraper.save_df(items, columns)
    scraper.close_site()


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

    def get_articles(self, search_word, mont):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-results__sectionContainer__34n_c")))
        news = self.driver.find_elements(By.XPATH, "//div[@class='search-results__sectionContainer__34n_c']//ul//li")
        current_dt = datetime.now()
        date_search = current_dt - relativedelta(months=max(0, mont - 1)) # current and previous
        date_search = date_search.replace(day=1) # get until the first date of specified month

        news_datetime = current_dt
        items = []

        while news_datetime > date_search:
            for idx, el in enumerate(news):
                actions = ActionChains(self.driver)
                actions.move_to_element(el).perform()
                news_date = el.find_element(By.CSS_SELECTOR, "time").get_attribute('datetime') 
                news_datetime = datetime.strptime(news_date, '%Y-%m-%dT%H:%M:%SZ')
                if news_datetime < date_search:
                    break

                title = el.find_element(By.XPATH, 'div/div/header').text
                
                news_date = news_datetime.strftime("%Y-%m-%d")
                pic_name = f'news_picture_{len(items)}'

                src_pic = el.find_element(By.TAG_NAME, 'img').get_attribute('src')
                download_driver = webdriver.Chrome()
                download_driver.get(src_pic)
                download_driver.save_screenshot(f"output/{pic_name}.png")
                download_driver.quit()

                count_phases = title.lower().count(search_word)
                money_in_title = re.search(r'$\d{2}\.\d|$[\d,]+\.\d{2}|\d+\s+dollars|\d+\s*USD', title)
                items.append([title, news_date, pic_name, count_phases, bool(money_in_title)])
            if news_datetime < date_search:
                break
            next_page_button = self.driver.find_elements(By.XPATH, "//div[@class='search-results__pagination__2h60k']//button")[-1]
            next_page_button.click()
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-results__sectionContainer__34n_c")))
            news = self.driver.find_elements(By.XPATH, "//div[@class='search-results__sectionContainer__34n_c']//ul//li")
        
        return items
    
    def save_df(self, items, col):
        df = pd.DataFrame(items, columns=col)
        df.to_excel("output/news.xlsx", index=False)

    def close_site(self):
        self.driver.close()

        



