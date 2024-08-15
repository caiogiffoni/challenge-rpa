import logging
from selenium import webdriver

def setup_logger():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger()

def download_img(src_pic, pic_name):
    download_driver = webdriver.Chrome()
    download_driver.get(src_pic)
    download_driver.save_screenshot(f"output/{pic_name}.png")
    download_driver.quit()
