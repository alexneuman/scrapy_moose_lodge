
from scrapy.utils.response import open_in_browser
from bs4 import BeautifulSoup
import json


def table_parse(table, rename_key_mapping:dict|None = None, partial_match=True) -> list[dict]:
    """Converts a table into a list of dictionaries with the headers as keys
        Optional `rename_key_mapping`: accepts a dictionary.
            If any of the keys partially match any of the table keys, the key will be renamed to the mapping's value
    """
    if rename_key_mapping is None:
        rename_key_mapping = {} 
    if table is None:
        return []
    headers = []
    data = []

    for header in table.xpath('.//tr[1]/th'):
        for k, v in rename_key_mapping.items():
            h = header.xpath('./text()|.//*[text()]/text()').get().replace('\n', '').lower().strip()
            if partial_match is True and k in h:
                headers.append(v)
                break
            elif partial_match is False and k == h:
                headers.append(v)
                break
        else:
            headers.append(header.xpath('./text()|.//*[text()]/text()').get().replace('\n', '').lower().strip())
    if not headers:
        return []
    
    for row in table.xpath('./tbody/tr')[1:]:
        # cell data
        cells = row.xpath('.//td')
        if len(cells) != len(headers):
            # table body cannot be parsed
            return []
        d = dict()
        for i, cell in enumerate(cells):
            item = cell.xpath('string(.)').get()
            d[headers[i]] = item
        data.append(d)
    return data