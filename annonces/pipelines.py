# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

class AnnoncesPipeline(object):

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['scrapy']
        self.collection = self.db['test-collection']

    def process_item(self, item, spider):
        try:
            self.collection.insert_one(dict(item))
        except:
            pass
        return item
