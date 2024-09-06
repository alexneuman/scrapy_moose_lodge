
import logging
from pathlib import Path
import os
from .request_block import should_abort_request
from scrapy.utils.reactor import install_reactor
install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

found = False
ENV_PATH = Path(__file__)

SPIDER_MIDDLEWARES = {
}

DOWNLOADER_MIDDLEWARES = {
    
}


logger = logging.getLogger(__name__)

DOWNLOADER_MIDDLEWARES.update({
        # 'generic.middlewares.ErrorLogsAPIMiddleware': 100
    })

PLAYWRIGHT_ENABLED = os.getenv('PLAYWRIGHT_ENABLED') in ('T', 't', True, 'true', 'True')

if PLAYWRIGHT_ENABLED:
    PLAYWRIGHT_MAX_CONTEXTS = int(os.environ.get('PLAYWRIGHT_MAX_CONTEXTS', 1000))
    PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = os.getenv('PLAYWRIGHT_MAX_PAGES_PER_CONTEXT', 1000)
    DOWNLOAD_HANDLERS = {
        "http": "generic.handler.PagePlusDownloadHandler",
        "https": "generic.handler.PagePlusDownloadHandler",
    }


    PLAYWRIGHT_CONTEXT_ARGS = {
        'ignore_https_errors':True,
        'wait_for_load_state': 'commit'
    }
    PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", '').lower() in ('true', '1', 't')
    PLAYWRIGHT_LAUNCH_OPTIONS = {'headless': PLAYWRIGHT_HEADLESS,
                                #  'ignore_https_errors': True,
                                #  'wait_for_load_state': 'domcontentloaded'
                                 }
    PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 90000
    PLAYWRIGHT_BROWSER_TYPE = os.getenv('PLAYWRIGHT_BROWSER', 'chromium')
    PLAYWRIGHT_RESOURCE_BLOCK = os.getenv('PLAYWRIGHT_RESOURCE_BLOCK', '').split(',')
    PLAYWRIGHT_ABORT_REQUEST = should_abort_request(
        PLAYWRIGHT_RESOURCE_BLOCK
        # 'script',
        # abort_url_patterns=['.*captcha.*']
        )

     

BOT_NAME = 'generic'

SPIDER_MODULES = ['generic.spiders']
NEWSPIDER_MODULE = 'generic.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum     rrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = int(os.environ.get('CONCURRENCY_PER_SPIDER', 1))

# LOGGING

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
# LOG_FILE = 'log'

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0 

REDIRECT_ENABLED = True
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 20
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = os.getenv('COOKIES_ENABLED', True) in (True, 'True', 'true', 't', 'T')

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9'
}

EXTENSIONS = {
}


ITEM_PIPELINES = {
}

#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# CACHE 
HTTPCACHE_ENABLED = os.getenv('HTTPCACHE_ENABLED', True) in (True, 'True', 'true', 't')
# HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [400, 403, 429, 500]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# HTTPCACHE_ALWAYS_STORE = True

# RETRY SETTINGS
RETRY_TIMES = os.getenv('RETRY_TIMES', 5)
RETRY_ENABLED = True
RETRY_HTTP_CODES = [408, 429, 400, 403, 500, 502, 503, 549]
HTTPERROR_ALLOWED_CODES = [403, 500, 502, 999]

TOR_ENABLED = os.getenv('TOR_ENABLED') in ('true', True, '1', 't')
if TOR_ENABLED:
    if PLAYWRIGHT_ENABLED:
        PLAYWRIGHT_LAUNCH_OPTIONS.update({
            'proxy': {
                'server': 'socks5://127.0.0.1:9050'
            }
        })
    DOWNLOADER_MIDDLEWARES.update(
        {
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
            # 'tor_ip_rotator.middlewares.TorProxyMiddleware': 100
        }
    )
    TOR_IPROTATOR_ENABLED = True
    TOR_IPROTATOR_CHANGE_AFTER = 20
    TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER = 1