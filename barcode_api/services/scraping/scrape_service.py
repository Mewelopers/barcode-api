import logging
from types import TracebackType
from typing import cast

from pyppeteer import browser, launch  # type: ignore
from pyppeteer_stealth import stealth  # type: ignore

from barcode_api.config import settings
from barcode_api.deps.common import Service
from barcode_api.schemas.products import ProductScrapeResult
from barcode_api.schemas.scraping import ScrapeDataCreate
from barcode_api.services.crud.scrape_data_crud import ScrapeDataCrud
from .exceptions import ProductNotFoundException, WebsiteNavigationException
from .html_parser import ProductHTMLParser, Selectors

logger = logging.getLogger(__name__)


class ScrapeService:
    """
    Service for scraping product information
    """

    def __init__(self, scrape_crud: ScrapeDataCrud = Service(ScrapeDataCrud)) -> None:
        """
        Initializes a new instance of the ScrapeService class.

        Args:
            scrape_crud (Injectable): ScrapeDataCrud instance
        """
        self.scrape_crud = scrape_crud

    async def setup(self) -> None:
        """
        Sets up the browser and page
        """
        self.browser = await launch(
            headless=True,
            executablePath=settings.BROWSER_PATH,
            stealth=True,
        )
        self.page = await self.browser.newPage()
        await stealth(self.page)

    async def __aenter__(self) -> "ScrapeService":
        logging.info("Launching new browser")
        await self.setup()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> bool | None:
        logging.info("Closing browser")
        await self.dispose()
        return None

    async def dispose(self) -> None:
        """
        Closes the browser and page
        """
        await cast(browser.Browser, self.browser).close()
        self.browser = None
        self.page = None

    @staticmethod
    def _url(barcode: str) -> str:
        return f"https://www.barcodelookup.com/{barcode}"

    async def _wait_for_page_load(self) -> None:
        """
        Wait for the footer to load, which is the last element on the page
        """
        await cast(browser.Page, self.page).waitForSelector(Selectors.footer, timeout=5000)

    async def _save_html(self, barcode: str) -> str:
        """
        Saves the HTML data to the database

        Args:
            barcode (str): Product barcode

        Returns:
            str: HTML string
        """
        html = await cast(browser.Page, self.page).content()

        scrape_data = ScrapeDataCreate(
            barcode=barcode,
            html=html,
            url=self._url(barcode),
        )
        await self.scrape_crud.create(obj_in=scrape_data)

        return html

    async def scrape(self, barcode: str) -> ProductScrapeResult:
        """
        Scrapes product information from the website

        Args:
            barcode (str): Product barcode

        Raises:
            RuntimeError: When the browser or page is not initialized
            WebsiteNavigationException: When the website navigation times out
            ProductNotFoundException: When the product is not found

        Returns:
            ProductScrapeResult: Product information
        """
        if self.browser is None or self.page is None:
            raise RuntimeError("ScrapeService not initialized")
        await self.page.goto(self._url(barcode))
        try:
            await self._wait_for_page_load()
        except TimeoutError as e:
            raise WebsiteNavigationException("Website navigation timed out") from e

        html = await self._save_html(barcode)
        parser = ProductHTMLParser(html, barcode)

        try:
            return await parser.collect()
        except ProductNotFoundException as e:
            raise ProductNotFoundException(barcode) from e
