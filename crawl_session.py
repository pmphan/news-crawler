import logging
import asyncio
from aiohttp import ClientSession, DummyCookieJar
from concurrent.futures import ProcessPoolExecutor

logger = logging.getLogger(__name__)

class CrawlSession:
    def __init__(self):
        """
        Async session helper class.
        Run blocking function, since BeautifulSoup parsing may take up CPU time.
        """
        # VnExpress will send us cached response even when we change page, category or date range query.
        # Disable cookie to bypass this.
        self._session = ClientSession(cookie_jar=DummyCookieJar())
        self._executor = ProcessPoolExecutor()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        """
        Exit from session.
        """
        await self._session.close()

    async def fetch(self, url, *args, **kwargs):
        """
        Fetch result from URL.

        Args:
            *args:
                Extra positional arguments for session.get
            **kwargs:
                Extra keyword arguments for session.get
        """
        async with self._session.get(url, *args, **kwargs) as response:
            logger.info("GET <%d> %s", response.status, response.url)
            response.raise_for_status()
            return await response.read()

    async def create_request(self, url, callback=None, cb_args=[], *args, **kwargs):
        """
        Create a request with callback.

        Args:
            url:
                URL of GET request.
            callback:
                Callback function to be called when request finished, take request output as arguments.
            cb_args:
                List of extra arguments to pass to call back function.
            *args:
                Extra positional arguments for GET request.
            **kwargs:
                Extra keyword arguments for GET request.
        """
        response = await self.fetch(url, *args, **kwargs)
        if callback:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self._executor, callback, response, *cb_args)
        return response
