import re
from time import sleep
from typing import Iterable

import scrapy
from scrapy import Request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from steam_scrapy.items import AppInfoItem, LanguageItem


class ReviewSpider(scrapy.Spider):
    name = "app_info"
    allowed_domains = ['store.steampowered.com', 'steamcommunity.com']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        options = webdriver.ChromeOptions()
        options.add_argument('--lang=en-US')
        self.driver = webdriver.Chrome(options=options)

        # define the target app ids to scrape. For example, 1245620 is the app id of Elden Ring
        self.app_ids = getattr(self, 'app_ids', '1245620').split(',')

    def start_requests(self) -> Iterable[Request]:
        for app_id in self.app_ids:
            url = f'https://store.steampowered.com/app/{app_id}/'
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        try:
            # open the page
            self.driver.get(response.url)
            self.driver.implicitly_wait(10)

            # if redirected, submit the age information
            if re.match(r'^https://store\.steampowered\.com/agecheck/app/\d+/$', self.driver.current_url):
                self.driver.find_element(By.ID, 'ageDay').send_keys('8')
                month_drop_down = self.driver.find_element(By.ID, 'ageMonth')
                Select(month_drop_down).select_by_value('August')
                self.driver.find_element(By.ID, 'ageYear').send_keys('2003')
                self.driver.find_element(By.ID, 'view_product_page_btn').click()

            item = AppInfoItem()
            # on the app page
            item['name'] = self.driver.find_element(By.CLASS_NAME, 'apphub_AppName').text
            search = re.search(
                r"^https://store\.steampowered\.com/app/(\d+)/[A-Za-z0-9_]+/$",
                self.driver.current_url)
            if search is not None:
                item['id'] = search.group(1)

            dev_rows = self.driver.find_elements(By.CSS_SELECTOR, '.glance_ctn_responsive_left > .dev_row > .summary')
            item['developer'] = dev_rows[0].text
            item['publisher'] = dev_rows[1].text

            item['release_date'] = self.driver.find_element(By.CSS_SELECTOR, '.release_date > .date').text

            item['description'] = self.driver.find_element(By.CLASS_NAME, 'game_description_snippet').text
            user_reviews = self.driver.find_elements(By.CSS_SELECTOR, '#userReviews > div > .summary')
            item['recent_reviews'] = user_reviews[0].text
            item['all_reviews'] = user_reviews[1].text

            # click to show those user defined tags
            self.driver.find_element(By.CLASS_NAME, 'add_button').click()
            # get those elements
            user_defined_tags = WebDriverWait(self.driver, 10).until(
                lambda d: d.find_elements(By.CLASS_NAME, 'app_tag_control')
            )
            item['user_defined_tags'] = [tag.text for tag in user_defined_tags]
            # close it
            self.driver.find_element(By.CSS_SELECTOR, '.newmodal_buttons > .btn_grey_steamui').click()

            item['labels'] = [label.text for label in self.driver.find_elements(By.CLASS_NAME, 'label')]

            try:
                # if the language button exists, click it to show all the languages
                all_language_btn = self.driver.find_element(By.CLASS_NAME, 'all_languages')
                all_language_btn.click()
            except Exception:
                pass


            language_option_rows = self.driver.find_elements(By.CSS_SELECTOR, '.game_language_options > tbody > tr')
            language_list = []
            for i in range(1, len(language_option_rows)):
                language_item = LanguageItem()
                tds = language_option_rows[i].find_elements(By.TAG_NAME, 'td')
                language_item['language'] = tds[0].text
                language_item['interface'] = len(tds[1].text) != 0
                language_item['full_audio'] = len(tds[2].text) != 0
                language_item['subtitles'] = len(tds[3].text) != 0
                language_list.append(language_item)
            item['languages'] = language_list

            try:
                # if the discount exists, get the discount price
                item['original_price'] = self.driver.find_element(By.CLASS_NAME, 'discount_original_price').text
                item['discount_final_price'] = self.driver.find_element(By.CLASS_NAME, 'discount_final_price').text
            except Exception:
                pass
                try:
                    # discount does not exist
                    item['original_price'] = self.driver.find_element(By.CLASS_NAME, 'game_purchase_price').text
                except Exception:
                    pass

            yield item
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.close('panic')

    def close(self, reason):
        self.driver.close()
        return super().close(self, reason)
