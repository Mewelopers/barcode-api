"""
html_parser.py

This module contains classes and functions for parsing HTML data and extracting product information.

Classes:
- Selectors: A class containing CSS selectors for extracting product information from HTML data.
- ProductHTMLParser: A class for parsing HTML data and extracting product information.

Functions:
- None

Exceptions:
- TagNotFoundException: An exception raised when a required HTML tag is not found.

"""
import logging

import httpx
from bs4 import BeautifulSoup

from barcode_api.schemas.products import ProductScrapeResult
from .exceptions import TagNotFoundException

logger = logging.getLogger(__name__)


class Selectors:
    """
    A class containing CSS selectors for extracting product information from HTML data.
    """

    product = "#product"
    product_details = f"{product} .product-details"
    ean_header = f"{product_details} > h1"
    product_title = f"{product_details} > h4"
    product_labels = f"{product_details} > .product-text-label"
    barcode_img = "#barcode-image svg"
    product_meta_data = ".product-meta-data"
    footer = ".footer"
    thumbnail = "div#largeProductImage img"


class ProductHTMLParser:
    """
    A class for parsing HTML data and extracting product information.
    """

    def __init__(self, html: str, barcode: str) -> None:
        """
        Initializes a new instance of the ProductHTMLParser class.

        Parameters:
        - html: A string representing the HTML data to parse.
        - barcode: A string representing the barcode of the product.
        """
        self.soap = BeautifulSoup(html, "html.parser")
        self.barcode = barcode

    def beautify(self, html: str) -> str:
        """
        Returns a prettified version of the HTML data.

        Parameters:
        - html: A string representing the HTML data to prettify.

        Returns:
        - A string representing the prettified HTML data.
        """
        return self.soap.prettify()

    def _get_product_name(self) -> str:
        """
        Returns the name of the product.

        Raises:
        - TagNotFoundException: If the product title tag is not found.

        Returns:
        - A string representing the name of the product.
        """
        element = self.soap.select_one(Selectors.product_title)
        if element is None:
            raise TagNotFoundException(f"Could not find product title for barcode {self.barcode}")
        return element.text.strip()

    def _get_barcode_image(self) -> bytes | None:
        """
        Returns the barcode image as bytes, or None if it is not found.

        Returns:
        - A bytes object representing the barcode image, or None if it is not found.
        """
        element = self.soap.select_one(Selectors.barcode_img)
        if element is None:
            logger.warning(f"Could not find barcode image for barcode {self.barcode}")
            return None
        # Can be converted to an PNG image, but it it actually needed?
        # can be mimified
        return bytes(element.prettify(), encoding="utf-8")

    def _get_product_meta_data(self, target_selector: str) -> dict | None:
        """
        Returns a dictionary containing the product metadata.

        Returns:
        - A dictionary containing the product metadata.
        """
        collection = self.soap.select_one(target_selector)
        if collection is None:
            logger.warning(f"Could not find product metadata for barcode {self.barcode}")
            return None

        entries = collection.select("div.product-text-label")

        data = {}
        for enrty in entries:
            value_tag = enrty.select_one("span")

            if value_tag is None:
                continue

            key_tag = value_tag.previous_sibling

            if key_tag is None:
                continue

            key = key_tag.text.split(":")[0].strip().lower()
            value = value_tag.text.strip()
            data[key] = value

        return data

    def _get_product_description(self) -> str | None:
        """
        Returns the description of the product.

        Returns:
        - A string representing the description of the product, or None if it is not found.
        """
        tags = self._get_product_meta_data(Selectors.product_meta_data)

        if tags is None:
            logger.warning(f"Could not find product description for barcode {self.barcode}")
            return None

        return tags.get("description", None)

    def _get_product_manufacturer(self) -> str | None:
        tags = self._get_product_meta_data(Selectors.product_details)
        if tags is None:
            logger.warning(f"Could not find product manufacturer for barcode {self.barcode}")
            return None

        return tags.get("manufacturer", None)

    async def _get_product_thumbnail(self) -> bytes | None:
        """
        Returns the manufacturer of the product.

        Returns:
        - A string representing the manufacturer of the product, or None if it is not found.
        """
        element = self.soap.select_one(Selectors.thumbnail)

        if element is None:
            logger.warning(f"Could not find product thumbnail for barcode {self.barcode}")
            return None

        src = element.attrs.get("src", None)

        if src is None:
            logger.warning(f"Could not find src attribute for product thumbnail for barcode {self.barcode}")
            return None

        async with httpx.AsyncClient() as client:
            response = await client.get(src)
            if response.status_code != 200:
                logger.warning(
                    f"Could not download product thumbnail {self.barcode}, status code {response.status_code}"
                )
                return None
            return response.content

    async def collect(self) -> ProductScrapeResult:
        """
        Collects the product information from the HTML data.

        Returns:
        - A ProductScrapeResult object containing the extracted product information.
        """
        return ProductScrapeResult(
            barcode=self.barcode,
            name=self._get_product_name(),
            barcode_image=self._get_barcode_image(),
            description=self._get_product_description(),
            manufacturer=self._get_product_manufacturer(),
            thumbnail=await self._get_product_thumbnail(),
        )
