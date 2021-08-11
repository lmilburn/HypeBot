import scrapy
import json
from datetime import datetime


class HypebeastbotSpider(scrapy.Spider):
    name = 'hypebeastbot'
    allowed_domains = ['hbx.com/archives/new-arrivals']
    start_urls = ['http://hbx.com/archives/new-arrivals/']

    def parse(self, response):
        itemDict = {}
        itemList = response.css("div.product-body")
        print("List up-to-date as of "+str(datetime.now()))
        for item in itemList:
            name = item.css("a.name::text")[0].get()
            price = item.css("span.regular-price::text").get()
            itemDict[name] = price
        with open("sample.json", "w") as outfile:
            json.dump(itemDict, outfile)
