from robocorp.tasks import task
from RPA.Robocorp.WorkItems import WorkItems

from config import CATEGORY, COLUMNS, LINK, MONTHS, SEARCH_TERM
from src.scraper import NewsScraper


@task
def execute_scraper():
    scraper = NewsScraper(LINK, SEARCH_TERM, CATEGORY, MONTHS, COLUMNS)
    scraper.open_site()
    scraper.search()
    scraper.category_filter()
    scraper.get_articles()
    scraper.save_df()
    scraper.close_site()