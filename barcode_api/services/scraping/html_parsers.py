import abc

from bs4 import BeautifulSoup


class ScrapeHTMLParser(abc.ABC):
    class Selectors:
        ...

    def __init__(self, html: str) -> None:
        self.soap = BeautifulSoup(html, "html.parser")

    def beautify(self, html: str) -> str:
        return self.soap.prettify()


class BarcodeLookupHTMLParser(ScrapeHTMLParser):
    class Selectors:
        product = "#product"
        product_details = f"${product} .product-details"
        ean_header = f"{product_details} > h1"
        product_title = f"{product_details} > h4"
        product_labels = f"{product_details} > .product-text-label"
        barcode_img = f"{product_details} > .barcode-image-box > barcode-image svg"
        product_meta_data = f"{product_details} > .product-meta-data"
        footer = ".footer"
