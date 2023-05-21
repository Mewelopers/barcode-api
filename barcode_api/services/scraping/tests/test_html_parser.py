import pytest

from ..html_parser import ProductHTMLParser


class TestProductHTMLParser:
    def test_collet_product_name(self, mock_product_html: tuple[str, str]) -> None:
        barcode, html = mock_product_html
        parser = ProductHTMLParser(html, barcode)

        assert parser._get_product_name() == "Winterfresh Original Guma Do Ucia Bez Cukru 35 G (25 Draetek)"

    def test_collect_barcode_image(self, mock_product_html: tuple[str, str]) -> None:
        barcode, html = mock_product_html
        parser = ProductHTMLParser(html, barcode)

        res = parser._get_barcode_image()

        assert res is not None
        assert res.startswith(b"<svg ")

    def test_collect_description(self, mock_product_html: tuple[str, str]) -> None:
        barcode, html = mock_product_html
        parser = ProductHTMLParser(html, barcode)

        res = parser._get_product_description()

        assert res is not None

    def test_collect_manufacturer(self, mock_product_html: tuple[str, str]) -> None:
        barcode, html = mock_product_html
        parser = ProductHTMLParser(html, barcode)

        res = parser._get_product_manufacturer()

        assert res is not None

    @pytest.mark.asyncio
    async def test_collect_thumbnail(self, mock_product_html: tuple[str, str]) -> None:
        barcode, html = mock_product_html
        parser = ProductHTMLParser(html, barcode)

        res = await parser._get_product_thumbnail()

        assert res is not None
        assert len(res) > 0
        assert isinstance(res, bytes)
