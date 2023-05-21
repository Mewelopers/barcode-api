class ParserException(Exception):
    pass


class TagNotFoundException(ParserException):
    pass


class ProductNotFoundException(ParserException):
    def __init__(self, barcode: str) -> None:
        super().__init__(f"Product with barcode {barcode} not found")
        self.barcode = barcode


class WebsiteNavigationException(ParserException):
    pass
