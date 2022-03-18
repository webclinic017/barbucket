import logging

from bs4 import BeautifulSoup


_logger = logging.getLogger(__name__)


class PageCountExtractor():
    def get_page_count(self, html: str) -> int:
        soup = BeautifulSoup(html, 'html.parser')
        pagination_tables = soup.find_all('ul', class_='pagination')
        page_buttons = pagination_tables[0].find_all('li')
        page_count = int(page_buttons[-2].text)
        # todo: handle errors
        return page_count
