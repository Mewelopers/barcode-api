import abc
from typing import ClassVar, Type

from pyppeteer.browser import Page

from .html_parsers import BarcodeLookupHTMLParser, ScrapeHTMLParser


class ScrapeStrategy(abc.ABC):
    parser: ClassVar[Type[ScrapeHTMLParser]]

    @abc.abstractmethod
    def target_url(self, target: str) -> str:
        ...

    @abc.abstractmethod
    async def scrape(self, page: Page) -> str:
        ...

    @classmethod
    def name(cls) -> str:
        return cls.__name__


class BarcodeLookupStrategy(ScrapeStrategy):
    parser: ClassVar[Type[BarcodeLookupHTMLParser]] = BarcodeLookupHTMLParser

    def target_url(self, barcode: str) -> str:
        return f"https://www.barcodelookup.com/{barcode}"

    async def scrape(self, page: Page) -> str:
        await page.waitForSelector(self.parser.Selectors.footer)
        html_contents = await page.content()
        html = self.parser(html_contents).beautify(html_contents)

        return html
