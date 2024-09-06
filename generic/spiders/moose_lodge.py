import re
import json
from time import sleep

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.utils.response import open_in_browser
from scrapy_playwright import *
from scrapy_playwright.page import PageMethod
from inputs.datasets import us_cities_dataset
from inputs.inputs import inputs_from_csv

import page.page_methods as pm

from scrapy import Request

class VASpider(scrapy.Spider):
    name = 'moose_lodge'
    seen = set()

    def start_requests(self):
        inputs = list(reversed(list(us_cities_dataset())))
        distances = [5, 10, 50, 100, 150]
        for distance in distances:
            for row in inputs:
                lat = row['lat']
                long = row['lon']
                url = f'https://www.mooseintl.org/route/single_ajax.php?lat={lat}&lng={long}&distance={distance}&rv=false&camping=false&smoke_free=false'
                # print(url)
                yield Request(
                    url=url,
                    dont_filter=True
                )           

    def parse(self, response):
        print('Got page', response.status, response.meta.get('download_slot', 'Pulling from cache...') or 'No cache found...')
        # print(response.url, response.request.url)
        # return
        # return
        results = response.selector.jmespath('data')

        for result in results:
            data = result.get()
            full_address = data['address']
            if full_address in self.seen:
                continue
            self.seen.add(full_address)
            description = data['description']
            city = ''
            state = ''
            street = ''
            zip_code = ''
            try:
                match = re.match(r'(.*), (.*),? (\w+) (\d+)', full_address)
                if match:
                    street, city, state, zip_code = match.groups()
                elif not match:
                    match = re.match(r'(.*), (.*),(\w+).* (\d+)', full_address)
                    if match:
                        street, city, state, zip_code = match.groups()
                elif not match:
                    match = re.match(r'(.*), (\w+) (\d+)', full_address)
                    if match:
                        street, state, zip_code = match.groups()
            except Exception as e:
                pass
                # print(full_address, ' BOB', e)
                # sleep(1000000)
            if len(zip_code) == 1:
                print(full_address, '\n', zip_code)
                # sleep(1000000)
            data['streetAddress'] = street
            data['city'] = city
            data['state'] = state
            data['zipCode'] = zip_code
            data['fullAddress'] = full_address
            try:
                data['phone'] = (re.search(r'Phone: (.*?)\r', description) or re.search(r'Phone:.*?(\(.*?)\\r', description)).group(1)
            except:
                pass
                # print(data)
                # sleep(100000)
            data['website'] = re.search(r'href=.(.*?)"', description).group(1)
            data['email'] = re.search(r'mailto:(.*?)"', description).group(1)
            if 'mailto' in data['website']:
                data['website'] = ''
            try:
                data['lodgeNumber'] = re.search(r'Lodge #(\d+)', description).group(1) 
            except:
                pass
                # print(data)
                # # sleep(1000000)
            data['phone'] = data['description'].split('"')[0].split('\r')[0].split('Phone: ')[-1]
            del data['address']
            del data['description']
            del data['distance']
            yield data
