from barcode_api.schemas.products import ProductCreate
from bs4 import BeautifulSoup


class Selectors:
    product = "#product"
    product_details = f"${product} .product-details"
    ean_header = f"{product_details} > h1"
    product_title = f"{product_details} > h4"
    product_labels = f"{product_details} > .product-text-label"
    barcode_img = f"{product_details} > .barcode-image-box > barcode-image svg"
    product_meta_data = f"{product_details} > .product-meta-data"
    footer = ".footer"


class ProductHTMLParser:
    def __init__(self, html: str) -> None:
        self.soap = BeautifulSoup(html, "html.parser")

    def beautify(self, html: str) -> str:
        return self.soap.prettify()

    async def collect(self) -> ProductCreate:
        raise NotImplementedError()
