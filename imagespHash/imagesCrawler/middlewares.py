# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from settings import USER_AGENT


class ImagesphashSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

   def process_request(self, request, spider):
        request.meta['proxy'] = USER_AGENT
