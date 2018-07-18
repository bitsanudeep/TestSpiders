import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import datetime

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader import XPathItemLoader
from scrapy.http.request import Request
from scrapy.item import Item
import logging,logaugment
from imagesCrawler.items import ImagesphashItem


class ImageSpider(CrawlSpider):
    name = "phash-spider"
    
    def __init__(self,*args, **kwargs):
        self.rules=(Rule(SgmlLinkExtractor(allow=(".",)),
	         callback='parse_item', follow=False),)
        super(ImageSpider, self).__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('start_url')] 
        # self.logger.
        # print "*****************url provide to crawl:%s******************"%self.start_urls
    
    def parse_item(self, response):                                            
        loader = XPathItemLoader(item = ImagesphashItem(), response = response)
        loader.add_xpath('image_urls', '//img/@src')   
        return loader.load_item()



