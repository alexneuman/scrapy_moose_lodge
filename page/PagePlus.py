
import json
from difflib import SequenceMatcher

import lxml

from playwright.async_api import Page, Locator


def _valid_json(txt: str):
    pass

def similar(a, b, cutoff=0.9):
    ratio =  SequenceMatcher(None, a, b).ratio()
    if ratio > cutoff:
        return True



class PagePlus:
    def __init__(self, page: Page):
        self.page = page
        # page.content = self.content
        self.captured = []
        self.request = None
        self._content = ''
        self._content_x = ''
        self.context_variables = dict()
        
        
    def __getattr__(self, attr: str):
        return getattr(self.page, attr)
    
    async def goto(self, url: str, *args, **kwargs):
        try:
            await self.super().goto(url, *args, **kwargs)
        except:
            print('REQUEST FAILED')
    
    def _get_context_xpath(self, path: str):
        if self.context_variables:
            return path.format_map(self.context_variables)
        return path

    def _get_context_variable(self, key):
        return self.context_variables[key]
    
    async def xpath(self, path: str) -> list[Locator]:
        path = self._get_context_xpath(path)
        locs = self.page.locator(path)
        elements_count = await locs.count()
        elements = []
        for i in range(elements_count):
            element = locs.nth(i)
            elements.append(element)
        return [el for el in elements]

    async def click(self, xpath, optional=False, timeout=30000, *args, **kwargs):
        xpath = self._get_context_xpath(xpath)
        try:
            await self.page.wait_for_selector(xpath, timeout=timeout, *args, **kwargs)
            button = self.page.locator(xpath).first
            print('Clicking button')
            await button.dispatch_event('click', timeout=timeout)

        except Exception as e:
            if optional:
                print('exception e', e)
                # await self.page.wait_for_timeout(1000000)
                return
            raise e

    async def scroll(self, path: str, optional=False, timeout=30000, *args, **kwargs):
        path = self._get_context_xpath(path)
        try:
            await self.page.wait_for_selector(path, timeout=timeout, state='attached')
            element = self.page.locator(path).first
        except Exception as e:
            if not optional:
                raise e
        await element.scroll_into_view_if_needed()
    


    async def fill(self, xpath: str, value: str|None = None, context_var: str | None =None,timeout=30000, *args, **kwargs):
        value = value or self._get_context_variable(context_var)
        await self.page.fill(xpath, value, timeout=timeout, *args, **kwargs)

    async def remove_element(self, xpath):
        xpath = self._get_context_xpath(xpath)
        el = await self.xpath(xpath)
        if el:
            await el[0].evaluate('(element) => element.remove()')

    async def scrollgone(self, xpath: str, timeout=30000, max_n=0, ms=10000, optional=False, break_xpath=None):
        i = 0
        while True:
            i+=1
            try:
                await self.scroll(xpath, optional=False, timeout=timeout)
                await self.page.wait_for_timeout(ms)
                if break_xpath:
                    element = self.page.locator(break_xpath)
                    if await element.count() > 0:
                        break
                print('Scrolled ', i)
            except Exception as e:
                print('HIT EXCEPTION', e)
                if not optional:
                    raise ValueError(e)
            if i == max_n: 
                print('BREAK')
                break
            


    
    async def clickgone(self, next_page_xpath: str, capture_xpaths: str|None = None, max_n=0, break_on_next_fail=False, optional=False, ms: int = 10000, click_retries = None, pause_on_click_fail = False, click_fail_count=5, click_fail_timeout=10000, cutoff=0.8):
        _click_retries = click_retries = click_retries or 5
        captured_html_elements: list[str] = []
        previous_last_html_element: str|None = None
        i = 0
        while True:
            print('Iterating')
            if click_retries == 0:
                break
            i+=1
            if capture_xpaths:
                elements = await self.xpath(capture_xpaths)
                current_html_elements = []
                print(f'Found {len(elements)} elements, on page {i}, total items: {len(captured_html_elements)}') 
                for element in elements:
                    html = await self.html_from_locator(element)
                    current_html_elements.append(html)
                current_last_html_element: str = current_html_elements[-1] if current_html_elements else '' # If the html is the same as the previous page, it was not a successful click
                
                if previous_last_html_element and similar(previous_last_html_element, current_last_html_element, cutoff=cutoff):
                    print('ELEMENTS ARE SIMILAR', f'Break flag', break_on_next_fail)
                    if not click_fail_count:
                        if break_on_next_fail:
                            print('Setting break flag')
                            break
                        print('Could not find Next')
                        # await self.page.wait_for_timeout(10000000)
                        # await self.page.context.close()
                        # await self.page.close()
                        # await self.page.wait_for_timeout(1000000)
                        raise ValueError('Could not successfully click next')
                    click_fail_count -= 1
                else:
                    click_fail_count = _click_retries
                
                previous_last_html_element = current_last_html_element
                
                for html in current_html_elements:
                    captured_html_elements.append(html)
                    
            if i > 1 and i >= max_n and max_n:
                break
            
            try:
                button = self.page.locator(next_page_xpath)
                print('Clicking button')
                await button.dispatch_event('click', timeout=click_fail_timeout)
                print('clciked button')

            except Exception as e:
                print('HIT EXCEPTION')
                if i == 1 and not optional:
                    raise ValueError(f'Click {next_page_xpath} not found')
                break
            
            await self.wait_for_timeout(ms)
            print(f'waiting for ${ms}')

        if capture_xpaths:
            print(f'WRITING ELEMENTS {len(captured_html_elements)}')
            self._write_elements_to_page(captured_html_elements)
            # yield self
            
    async def html_from_locator(self, loc: Locator):
        html =  await loc.evaluate('(element) => element.outerHTML')
        return html

    async def text_from_locator(self, loc: Locator):
        return await loc.text_content()
        
    async def goto(self, url: str, *args, **kwargs):
        try:
            await self.page.goto(url,  *args, **kwargs)
        except Exception as e:
            raise e
        return
        
    def _write_elements_to_page(self, elements: list[str]):
        # html_elements = [await self.html_from_locator(el) for el in elements]
        html_body = ''.join(elements)
        html = f'<html>{html_body}</html>'
        self.set_content(html)
        self._content = html
        # await self.page.evaluate(f'()=>document.body.innerHTML={html}')

    def set_content(self, content: str):
        self._content = content
        self.page._content = content

    async def write_html_to_file(self, file=None):
        with open(file or 'bob.html', 'w') as f:
            content = await self.page.content()
            f.write(content)

    def content(self):
        if self.captured and len(self.captured) == 1:
            data = json.loads(self.captured[0])
            return json.dumps(data)
        if self.captured and len(self.captured) > 1:
            data = [json.loads(i) for i in self.captured]
            return f'[{",".join(json.dumps(d) for d in data)}]'
        return self._content_x or self._content
            # or await self.page.content()
            
    async def handle_response(self, response, text, page):
        if text in response.url:
            # self.set_content(await response.text())
            self.captured.append(await response.text())
        
    async def wait_for_selector(self, xpath, visible = False, optional=False, *args, **kwargs):
        xpath = self._get_context_xpath(xpath)
        try:
            state = 'visible' if visible else 'attached'
            await self.page.wait_for_selector(xpath, state=state, *args, **kwargs)
        except Exception as e:
            if optional:
                return
            raise e

    async def capture_var(self, variable_name, xpath, optional=False, rm_txt: str|None = None):
        locs = await self.xpath(xpath)
        if not locs:
            if not optional:
                raise ValueError(f'Could not set variable ')
            val = ''
        else:
            val = await locs[0].inner_text()
        if rm_txt:
            val = val.replace(rm_txt, '')
        print(f'Set context variable: {variable_name}: {val}')
        self.context_variables[variable_name] = val
        
