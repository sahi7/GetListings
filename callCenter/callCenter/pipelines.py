# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class CallcenterPipeline:
    def __init__(self):
        self.existing_tel = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['Telephone'] in self.existing_tel:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.existing_tel.add(adapter['Telephone'])
            return item
