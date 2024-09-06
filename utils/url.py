
from urllib.parse import unquote
import re
import csv
from typing import Iterable

def google_decode(url):
    """
    Decode a google url.
    """
    if 'url=' not in url:
        return url
    url = re.sub(r'.*url=', '', url)
    url =re.sub(r'&.*', '', url)
    url = unquote(url)
    return url

def google_url(search_term: str, site: str|None = None, num_pages: int = 1) -> list[str]:
    """
    Get a google url for a search term.
    Optionally, specify a domain to search (e.g 'linkedin.com').
    """
    search_term_cleaned = search_term.replace('&', '%26').replace(" ", "+").replace(',','+').replace('++', '+')
    url = f'https://www.google.com/search?q={search_term_cleaned}'
    if site:
        url += f'+site%3A{site}'
    urls = [url]
    if num_pages > 1:
        for i in range(1, num_pages):
            urls.append(url + f'&start={i * 10}')
        return urls
    return urls

def starting_urls_from_file(file):
    """
        Returns a dictionary of the file.
        Args:
            - file: The file name
    """
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        return tuple(reader)