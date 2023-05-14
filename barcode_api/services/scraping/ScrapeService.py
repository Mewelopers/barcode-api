import abc
import logging
from types import TracebackType

from barcode_api.config import settings
from barcode_api.schemas.scraping import ScrapeResultCreate
from pyppeteer import launch
from pyppeteer_stealth import stealth

from .strategy import ScrapeStrategy

logger = logging.getLogger(__name__)


class ScrapeService(abc.ABC):
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
        await self.browser.close()
        self.browser = None
        self.page = None

    @abc.abstractmethod
    async def scrape(self, target: str, /, strategy: ScrapeStrategy) -> ScrapeResultCreate:
        ...


class BarcodeScraperService(ScrapeService):
    async def scrape(self, barcode: str, /, strategy: ScrapeStrategy) -> ScrapeResultCreate:
        if self.browser is None or self.page is None:
            raise RuntimeError("ScrapeService not initialized")
        url = strategy.target_url(barcode)
        await self.page.goto(url)

        html = await strategy.scrape(self.page)

        return ScrapeResultCreate(barcode=barcode, scrape_strategy=strategy.name(), url=url, html=html)
