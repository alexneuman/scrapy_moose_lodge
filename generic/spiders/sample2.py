import re
import json

import scrapy
from scrapy.utils.response import open_in_browser
from scrapy_playwright.page import PageMethod
from inputs.datasets import zips_dataset

import page.page_methods as pm



class AGChurchSpider(scrapy.Spider):
    name = "sample_2"
    seen = set()

    def start_requests(self):
        inputs = zips_dataset(step=10)
        for row in inputs:
            search_zip = row['zip']
            url = f'https://ag.org/Resources/Directories/Find%20a%20Church?Q={search_zip}'
            yield scrapy.Request(
                url=url,
                callback=self.get_pagination,
                method="GET",
                dont_filter=True,
                meta={
                    'playwright': True,
                    # 'playwright_context': url,
                    'playwright_page_methods': [
                        # PageMethod('wait_for_timeout', 30000000),
                        pm.wait_for_selector('//h1[.="Church Directory"]', optional=False, timeout=8000),
                        # pm.wait_for_timeout(3000),
                
                    ]
                    },
            )

    def get_pagination(self, response):
        num_pages_str = response.xpath('string((//ul[@class="pagination"])//li[not(./a[@aria-label])][last()])').get()
        if num_pages_str:
            num_pages = int(num_pages_str)
        else:
            num_pages = 0  
        for i in range(1, num_pages):
            url = response.request.url + f'&page={i}'
            yield response.follow(
                    url=url,
                    method="GET",
                    dont_filter=True,
                    callback=self.parse_pagination,
                    meta={
                        'playwright': True,
                        # 'playwright_context': url,
                        'playwright_page_methods': [
                            # PageMethod('wait_for_timeout', 5000000),
                            pm.wait_for_selector('//h1[.="Church Directory"]', optional=False, timeout=8000),
                        ]
                        })
        
    def parse_pagination(self, response):
        for result in response.xpath('//div[@class="panel panel-sm"]'):
            name = result.xpath('.//h3/text()').get()
            if name in self.seen:
                continue
            self.seen.add(name)
            d = dict()
            url = result.xpath('.//a/@href').get()
            d['church_website'] = result.xpath('.//i[@class="fa fa-fw fa-link"]/following-sibling::a/@href').get()
            d['email'] = response.xpath('.//i[@class="fa fa-fw fa-envelope"]/following-sibling::a/@href').get(default='').replace('mailto:', '')
            
            # if d['email']:
            #     open_in_browser(response)
            #     raise CloseSpider()
            yield response.follow(
                    url=url,
                    method="GET",
                    dont_filter=True,
                    callback=self.parse_details,
                    cb_kwargs=dict(d=d),
                    meta={
                        'playwright': True,
                        # 'playwright_context': url,
                        'playwright_page_methods': [
                            # PageMethod('wait_for_timeout', 5000000),
                            pm.wait_for_selector('//div[@class="formatted-content"]/h1', optional=False, timeout=8000),
                            # pm.wait_for_selector('//div[@class="google-maps-link"]')
                        ]
                        }) 

    def parse_details(self, response, d):
        d['location_name'] = response.xpath('string(//h1)').get()
        d['reverend_name'] = response.xpath('string(//h1/following-sibling::h5)').get()
        d['phone'] = response.xpath('//span[@class="list-text"][./i]/text()').get(default='').strip()
        d['street_address'] = response.xpath('//h4[.="Location"]/following-sibling::p/text()[1]').get().strip()
        # d['overall_rating'] = response.xpath('//div[@class="review-number"]/text()').get(default='')
        # d['number_ratings'] = response.xpath('string(//a[@class="review-box-link"])').get(default=0).split(' ')[0]
        city, state_zip = response.xpath('//h4[.="Location"]/following-sibling::p/text()[2]').get().replace('  ', '').replace('\n', '').split(',')
        state, zip_code = state_zip.replace('  ', ' ').strip().split(' ')
        d['state'] = state
        d['city'] = city
        d['zip'] = zip_code
        d['details_url'] = response.url
        # s = response.xpath('//div[@class="google-maps-link"]')
        # .re(r'll=(.*?),(.*?)&')

        yield d