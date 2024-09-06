
import json
import os
import re
import logging


import scrapy
from scrapy.utils.response import open_in_browser
from scrapy_playwright.page import PageMethod

from scrapy import Request
from inputs.dataset_files import *

class AppleJobs(scrapy.Spider):
    name = 'sample_1'
    start_urls = ['https://jobs.apple.com/en-us/search?location=&page=1']
    handle_httpstatus_list = [502, 404, 403, 438]
    # seen = DistributedSet(name)


    def parse(self, response):
        num_pages = int(response.xpath('(//span[@class="pageNumber"])[last()]/text()').get())
        for i in range(1, num_pages+1):
            print(i)
            url = f'https://jobs.apple.com/en-us/search?location=&page={i}'
            yield scrapy.Request(url=url, callback=self.parse_pagination,
                                 meta={
                                     'playwright': True,
                                     'playwright_page_methods': [
                                         PageMethod('wait_for_selector', '//h2')
                                     ]
                                 }
                                 )
            
    def parse_pagination(self, response):
        for listing in response.xpath('//tbody'):
            url = listing.xpath('.//a/@href').get()
            yield response.follow(url, callback=self.parse_listing, meta={
                                     'playwright': True,
                                     'playwright_page_methods': [
                                         PageMethod('wait_for_selector', '//h2[.="Summary"] | //div[text()="Sorry, this role does not exist or is no longer available."]')
                                     ]
                                 })
            
    def parse_listing(self, response):
        d = {}
        if response.xpath('//div[text()="Sorry, this role does not exist or is no longer available."]'):
            return
        d['summary'] = response.xpath('string(//div[@id="jd-job-summary"])').get()
        logging.debug(d)
        yield d
    