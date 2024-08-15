import re
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .utils import download_img, setup_logger

logger = setup_logger()


class NewsScraper:
    def __init__(self, url, search_term, category, months, columns):
        self.url = url
        self.search_term = search_term
        self.category = category
        self.months = months
        self.columns = columns
        self.driver = webdriver.Chrome()
        self.items = []

    def open_site(self):
        self.driver.get(self.url)
        logger.info(f"Opened site: {self.url}")

    def search(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-bar__icon__ORXTq")))
        self.driver.find_element(By.CLASS_NAME, "search-bar__icon__ORXTq").click()
        input = self.driver.find_element(By.TAG_NAME, 'input')
        input.send_keys(self.search_term)
        input.send_keys(Keys.RETURN)
        logger.info(f"Searched completed: {self.search_term}")


    def category_filter(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "sectionfilter")))
        dropdown = self.driver.find_element(By.XPATH,"//*[@id='sectionfilter' and self::button]")
        dropdown.send_keys(self.category)
        logger.info(f"Category filtered: {self.category}")


    def get_articles(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-results__sectionContainer__34n_c")))
        news = self.driver.find_elements(By.XPATH, "//div[@class='search-results__sectionContainer__34n_c']//ul//li")
        current_dt = datetime.now()
        date_search = current_dt - relativedelta(months=max(0, self.months - 1)) # current and previous
        date_search = date_search.replace(day=1) # get until the first date of specified month

        news_datetime = current_dt
        items = []

        i = 1
        while news_datetime > date_search:
            logger.info(f"Going to page {i}")
            for el in news:
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
                download_img(src_pic, pic_name)

                count_phases = title.lower().count(self.search_term)
                money_in_title = re.search(r'\$[\d,]+\.\d{1,2}|[\d,]+\s+dollars|[\d,]+\s+USD', title) # only accounting for the proposed formats.
                items.append([title, news_date, pic_name, count_phases, bool(money_in_title)])
            next_page_button = self.driver.find_elements(By.XPATH, "//div[@class='search-results__pagination__2h60k']//button")[-1]
            if news_datetime < date_search or next_page_button.get_attribute('disabled'): # if older news or last page, break
                break
            next_page_button.click()
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-results__sectionContainer__34n_c")))
            news = self.driver.find_elements(By.XPATH, "//div[@class='search-results__sectionContainer__34n_c']//ul//li")
            i+=1
        
        self.items = items
        logger.info(f"Items saved")

    
    def save_df(self):
        df = pd.DataFrame(self.items, columns=self.columns)
        df.to_excel("output/news.xlsx", index=False)
        logger.info(f"Excel Sile saved: output/news.xlsx")


    def close_site(self):
        self.driver.close()
        logger.info(f"Driver closed")

        