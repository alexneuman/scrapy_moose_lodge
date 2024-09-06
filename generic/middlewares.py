# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from contextlib import suppress
from time import sleep
import types
import csv
from logging import getLogger, Logger
from urllib.parse import urlparse
import json
import os
import gzip
from pathlib import Path
import pickle
import subprocess
import sys
from time import time
import logging

from scrapy.extensions.httpcache import FilesystemCacheStorage
from scrapy import signals, Spider, Request, Spider, Item
from scrapy.exceptions import IgnoreRequest, CloseSpider
from scrapy.core.scheduler import Scheduler
from scrapy.downloadermiddlewares.retry import RetryMiddleware, get_retry_request
from scrapy.http import HtmlResponse, Request
from scrapy.utils.request import fingerprint
from scrapy.utils.request import request_fingerprint
from scrapy.utils.python import to_bytes
# import zlib
from page.PagePlus import PagePlus
# from scrapy_selenium import SeleniumRequest
from playwright.async_api import Error as PlaywrightError
import requests

from utils.dict_parser import JsonResponseParser

from w3lib.http import headers_raw_to_dict, headers_dict_to_raw

# from utils.cookies import dict_from_cookie_string, open_native_chrome_and_fetch_cookie_from_url
# from utils.pia import change_server_forever, get_connection_status

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from generic.settings import logger, HTTPCACHE_DIR

class FlareSolverMiddleware:

    def process_request(self, request, spider):
        print('PROCESSING REQUEST')
        if self.i % 10 == 0 or True:
            url = "http://localhost:8191/v1"
            bob=request.url,
            headers = {"Content-Type": "application/json"}
            data = {
                "cmd": f"request.{request.method.lower()}",
                "url": '',
                "maxTimeout": 60000
            }
            response = requests.post(url, headers=headers, json=data)
            response_data = json.loads(response.text)
            user_agent = response_data['solution']['userAgent']
            headers = response_data['solution']['headers']
            cookies_lst = response_data['solution']['cookies']
            cookies = {}
            for cookie in cookies_lst:
                cookies[cookie['name']] = cookie['value']
            headers = {
            'User-Agent': user_agent
        }
            cookies = {
                    "KP_UIDz": cookies['KP_UIDz']
            }
            request.cookies.update(cookies)
            request.headers['User-Agent'] = user_agent
            sleep(3)
        self.i += 1