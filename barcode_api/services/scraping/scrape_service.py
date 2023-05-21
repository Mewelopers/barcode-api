import logging
from types import TracebackType
from typing import cast

from barcode_api.config import settings
from barcode_api.deps.common import Service
from barcode_api.schemas.products import ProductCreate
from barcode_api.schemas.scraping import ScrapeDataCreate
from barcode_api.services.crud.scrape_data_crud import ScrapeDataCrud
from pyppeteer import browser, launch  # type: ignore
from pyppeteer_stealth import stealth  # type: ignore

from .html_parser import ProductHTMLParser, Selectors

logger = logging.getLogger(__name__)


class ScrapeService:
    def __init__(self, scrape_crud: ScrapeDataCrud = Service(ScrapeDataCrud)) -> None:
        self.scrape_crud = scrape_crud

    async def setup(self) -> None:
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
        await cast(browser.Browser, self.browser).close()
        self.browser = None
        self.page = None

    @staticmethod
    def _url(barcode: str) -> str:
        return f"https://www.barcodelookup.com/{barcode}"

    async def _wait_for_page_load(self) -> None:
        """Wait for the footer to load, which is the last element on the page"""
        await cast(browser.Page, self.page).waitForSelector(Selectors.footer)

    async def _save_html(self, barcode: str) -> str:
        html = await cast(browser.Page, self.page).content()

        scrape_data = ScrapeDataCreate(
            barcode=barcode,
            html=html,
            url=self._url(barcode),
        )
        await self.scrape_crud.create(obj_in=scrape_data)

        return html

    async def scrape(self, barcode: str) -> ProductCreate:
        if self.browser is None or self.page is None:
            raise RuntimeError("ScrapeService not initialized")
        await self.page.goto(self._url(barcode))
        await self._wait_for_page_load()

        html = await self._save_html(barcode)
        parser = ProductHTMLParser(html, barcode)

        return await parser.collect()
