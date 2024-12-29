# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import re

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ReviewPipeline:
    def process_item(self, item, spider):
        item['hours'] = item['hours'].split(' ')[0]
        item['date_posted'] = ' '.join(item['date_posted'].split(' ')[1:3])
        pattern = r"^Posted: .+\n(Product received for free\n\n)?(Product refunded\n\n)?"
        search = re.search(pattern, item['content'])
        item['received_for_free'] = search.group(1) is not None
        item['refunded'] = search.group(2) is not None
        item['content'] = re.sub(pattern, '', item['content'])
        return item
