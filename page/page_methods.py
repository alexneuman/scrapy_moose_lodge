
from scrapy_playwright.page import PageMethod

    
def click(xpath, optional=False, timeout=30000, *args, **kwargs):
     return PageMethod('click', xpath=xpath, optional=optional, timeout=timeout, *args, **kwargs)

def fill(xpath: str, value: str|None = None, context_var: str | None =None,timeout=30000, *args, **kwargs):
    if not value and not context_var:
        print(value, context_var)
        raise ValueError('Must select a fill value option: value or context_var')
    return PageMethod('fill', xpath, value, context_var=context_var, timeout=timeout, *args, **kwargs)

def clickgone(next_page_xpath: str, capture_xpaths: str|None = None, max_n=0, break_on_next_fail=False, optional=False, ms: int = 10000, click_retries = None, pause_on_click_fail = False, click_fail_count=5, click_fail_timeout=10000, cutoff=0.8):
    return PageMethod('clickgone', next_page_xpath=next_page_xpath, capture_xpaths=capture_xpaths, max_n=max_n, break_on_next_fail=break_on_next_fail, optional=optional, ms=ms, click_retries=click_retries, pause_on_click_fail=pause_on_click_fail, click_fail_count=click_fail_count, click_fail_timeout=click_fail_timeout, cutoff=cutoff)
        
def goto(url: str, *args, **kwargs):
    return PageMethod('goto', url=url, *args, **kwargs)
    
def wait_for_selector(xpath, optional=False, visible=False, *args, **kwargs):
    return PageMethod('wait_for_selector', xpath=xpath, visible=visible, optional=optional, *args, **kwargs)

def remove_element(xpath, optional=False):
    return PageMethod('remove_element', xpath=xpath)

def capture_var(variable_name, xpath, optional=False, rm_txt=None):
    return PageMethod('capture_var', variable_name=variable_name, xpath=xpath, optional=optional, rm_txt=rm_txt)
    
def wait_for_timeout(timeout: int):
    return PageMethod('wait_for_timeout', timeout=timeout)

def write_html_to_file(file: str | None = None):
    return PageMethod('write_html_to_file', file=file)

def scroll(xpath, optional=False, timeout=30000):
    return PageMethod('scroll', path=xpath, optional=optional, timeout=timeout)

def scrollgone(xpath, timeout=30000, max_n=0, break_on_next_fail=False, optional=False, ms=10000, pause_on_fail=False, scroll_fail_count=5, break_xpath=None):
    return PageMethod('scrollgone', xpath=xpath, timeout=timeout, max_n=max_n, optional=optional, ms=ms, break_xpath=break_xpath)