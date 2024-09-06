
import logging
from time import time
from contextlib import suppress
from functools import partial

from scrapy_playwright.handler import ScrapyPlaywrightDownloadHandler
from page.PagePlus import PagePlus
from playwright_stealth.stealth import stealth_async
from scrapy_playwright.page import PageMethod
from scrapy_playwright.handler import _maybe_await, _encode_body, _make_response_logger, _make_request_logger
from scrapy_playwright.handler import _set_redirect_meta
from scrapy.responsetypes import responsetypes
from scrapy.exceptions import ScrapyDeprecationWarning
from scrapy.http.headers import Headers
from scrapy.http import Request, Response
from scrapy.utils.project import get_project_settings
from ipaddress import ip_address
from playwright.async_api import (
    Page,
    Response as PlaywrightResponse
)
from scrapy_playwright._utils import (
    _encode_body,
    _maybe_await,
)

logger = logging.getLogger("scrapy-playwright")
DEFAULT_CONTEXT_NAME = "default"


class PagePlusDownloadHandler(ScrapyPlaywrightDownloadHandler):
     

    async def _apply_page_methods(self, page: Page, request, spider) -> None:

        context_name = request.meta.get("playwright_context")
        page_methods = request.meta.get("playwright_page_methods") or ()

        if isinstance(page_methods, dict):
            page_methods = page_methods.values()
        for pm in page_methods:
            try:
                method = getattr(page, pm.method)
            except Exception as ex:
                    logger.warning(
                        "Ignoring %r: could not find method",
                        pm,
                        extra={
                            "spider": spider,
                            "context_name": context_name,
                            "scrapy_request_url": request.url,
                            "scrapy_request_method": request.method,
                            "exception": ex,
                        },
                        exc_info=True,
                    )
            else:
                pm.result = await _maybe_await(method(*pm.args, **pm.kwargs))
                await page.wait_for_load_state(timeout=self.config.navigation_timeout)
   
    async def _create_page(self, request, spider):
        """Create a new page in a context, also creating a new context if necessary."""
        context_name = request.meta.setdefault("playwright_context", DEFAULT_CONTEXT_NAME)
        # this block needs to be locked because several attempts to launch a context
        # with the same name could happen at the same time from different requests
        
        async with self.context_launch_lock:
            ctx_wrapper = self.context_wrappers.get(context_name)
            if ctx_wrapper is None:
                ctx_wrapper = await self._create_browser_context(
                    name=context_name,
                    context_kwargs=request.meta.get("playwright_context_kwargs"),
                    spider=spider,
                )

        await ctx_wrapper.semaphore.acquire()

        page_orig = await ctx_wrapper.context.new_page()
        # await stealth_async(page_orig)
        page = PagePlus(page_orig)
        self.stats.inc_value("playwright/page_count")
        total_page_count = self._get_total_page_count()
        logger.debug(
            "[Context=%s] New page created, page count is %i (%i for all contexts)",
            context_name,
            len(ctx_wrapper.context.pages),
            total_page_count,
            extra={
                "spider": spider,
                "context_name": context_name,
                "context_page_count": len(ctx_wrapper.context.pages),
                "total_page_count": total_page_count,
                "scrapy_request_url": request.url,
                "scrapy_request_method": request.method,
            },
        )
        self._set_max_concurrent_page_count()
        if self.config.navigation_timeout is not None:
            page.set_default_navigation_timeout(self.config.navigation_timeout)
        
        response_parse = request.meta.get('response_parse')
        if response_parse:
            url_text = response_parse['url_text']
            page.on('response', partial(page.handle_response, text=url_text, page=page))

        page.on("close", self._make_close_page_callback(context_name))
        page.on("crash", self._make_close_page_callback(context_name))
        page.on("request", _make_request_logger(context_name, spider))
        page.on("response", _make_response_logger(context_name, spider))
        page.on("request", self._increment_request_stats)
        page.on("response", self._increment_response_stats)
        
        return page

    async def _download_request_with_page(
        self, request: Request, page: Page, spider: Spider
    ) -> Response:
        # set this early to make it available in errbacks even if something fails
        if request.meta.get("playwright_include_page"):
            request.meta["playwright_page"] = page

        start_time = time()
        response, download = await self._get_response_and_download(request, page, spider)
        if isinstance(response, PlaywrightResponse):
            await _set_redirect_meta(request=request, response=response)
            headers = Headers(await response.all_headers())
            headers.pop("Content-Encoding", None)
        elif not download:
            logger.warning(
                "Navigating to %s returned None, the response"
                " will have empty headers and status 200",
                request,
                extra={
                    "spider": spider,
                    "context_name": request.meta.get("playwright_context"),
                    "scrapy_request_url": request.url,
                    "scrapy_request_method": request.method,
                },
            )
            headers = Headers()

        await self._apply_page_methods(page, request, spider)
        body_str = page.content() or await page.page.content()
        request.meta["download_latency"] = time() - start_time

        server_ip_address = None
        if response is not None:
            request.meta["playwright_security_details"] = await response.security_details()
            with suppress(KeyError, TypeError, ValueError):
                server_addr = await response.server_addr()
                server_ip_address = ip_address(server_addr["ipAddress"])

        if download and download.exception:
            raise download.exception

        if not request.meta.get("playwright_include_page"):
            await page.close()
            self.stats.inc_value("playwright/page_count/closed")

        if download:
            request.meta["playwright_suggested_filename"] = download.suggested_filename
            respcls = responsetypes.from_args(url=download.url, body=download.body)
            return respcls(
                url=download.url,
                status=download.response_status,
                headers=Headers(download.headers),
                body=download.body,
                request=request,
                flags=["playwright"],
            )
        body, encoding = _encode_body(headers=headers, text=body_str)
        respcls = responsetypes.from_args(headers=headers, url=page.url, body=body)
        return respcls(
            url=page.url,
            status=response.status if response is not None else 200,
            headers=headers,
            body=body,
            request=request,
            flags=["playwright"],
            encoding=encoding,
            ip_address=server_ip_address,
        )