from pathlib import Path

import pytest


@pytest.fixture
def mock_product_html() -> tuple[str, str]:
    return ("4009900382250", (Path(__file__).parent / "data/4009900382250.html").read_text())
