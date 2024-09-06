
from functools import partial, wraps
from typing import Literal
import re

from functools import partial
from typing import Literal
def should_abort_request(*args: Literal['image', 'media', 'script', 'stylesheet', 'font', 'xhr', 'socket', 'document', 'texttrack', 'fetch', 'eventsource', 'manifest', 'other'], abort_url_patterns:list[str]|None = None):
    def inner(request, args):
        if not args:
            return False
        return request.resource_type in args or ('.png' in request.url or '.jpg' in request.url and 'image' in args)
    return partial(inner, args=args)