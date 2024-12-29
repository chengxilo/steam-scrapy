from time import sleep
from typing import Iterable

import scrapy
from scrapy import Request
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from steam_scrapy.items import ReviewItem


class ReviewSpider(scrapy.Spider):
    name = "review"
    allowed_domains = ["steamcommunity.com"]

    custom_settings = {
        'ITEM_PIPELINES': {
            'steam_scrapy.pipelines.ReviewPipeline': 300,
        }
    }

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        options = webdriver.ChromeOptions()
        options.add_argument('--lang=en-US')
        self.driver = webdriver.Chrome(options=options)
        self.review_amount = 0

        # define how many reviews to scrape
        self.amount_limit = int(getattr(self, 'amount_limit', '100'))
        # define the target app id, for example, 1245620 is the app id of Elden Ring
        self.app_id = getattr(self, 'app_id', '1245620')
        # define the language of the reviews
        self.language = getattr(self, 'language', 'english')

    def start_requests(self) -> Iterable[Request]:
        url = f'https://steamcommunity.com/app/{self.app_id}/reviews/'
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        try:
            cnt = 0
            self.driver.get(response.url)
            self.driver.implicitly_wait(10)

            # set the filter
            # set language filter
            self.driver.find_element(By.ID, 'filterlanguage').click()
            language_opts = WebDriverWait(self.driver, 10).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, '.filterselect_options.language.shadow_content > div')
            )
            for opt in language_opts:
                if opt.text.lower() == self.language.lower():
                    opt.click()
                    break

            page = 1

            # page by page, get the reviews.
            while True:
                cards = self.driver.find_elements(By.CSS_SELECTOR, f'#page{page} .apphub_CardRow .apphub_Card')
                for card in cards:
                    review = ReviewItem()
                    review['title'] = card.find_element(By.CLASS_NAME, 'title').text
                    review['hours'] = card.find_element(By.CLASS_NAME, 'hours').text
                    review['date_posted'] = card.find_element(By.CLASS_NAME, 'date_posted').text
                    review['content'] = card.find_element(By.CLASS_NAME, 'apphub_CardTextContent').text
                    yield review
                    cnt += 1
                    if cnt >= self.amount_limit:
                        break
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                if len(cards) == 0:
                    break
                page += 1
                if cnt >= self.amount_limit:
                    break
        except Exception as e:
            self.logger.error(e)
            self.close('error')

    def close(self, reason):
        self.driver.close()
        return super().close(self, reason)

        pass
