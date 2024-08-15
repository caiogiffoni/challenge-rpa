from robocorp.browser import browser
from robocorp.tasks import task

from config import CATEGORY, COLUMNS, LINK, MONTHS, SEARCH_TERM
from src.NewsScraper import NewsScraper

# from RPA.Robocorp.WorkItems import WorkItems


@task
def execute_scraper():
    scraper = NewsScraper(LINK, SEARCH_TERM, CATEGORY, MONTHS, COLUMNS)
    scraper.set_webdriver()
    scraper.open_site()
    scraper.search()
    scraper.category_filter()
    scraper.get_articles()
    scraper.save_df()
    scraper.close_site()