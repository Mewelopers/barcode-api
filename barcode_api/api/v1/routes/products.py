import logging
from http import HTTPStatus

from barcode_api.deps.common import Repository, Service
from barcode_api.repositories.ScrapeResultRepository import ScrapeResultRepository
from barcode_api.schemas.products import ProductSearch
from barcode_api.services.scraping import strategy
from barcode_api.services.scraping.ScrapeService import BarcodeScraperService
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/products", tags=["products"])
logger = logging.getLogger(__name__)


@router.get("/{barcode}", response_class=HTMLResponse)
async def get_product(
    barcode: str,
    scraper: BarcodeScraperService = Service(BarcodeScraperService),
    repository: ScrapeResultRepository = Repository(ScrapeResultRepository),
) -> str:
    try:
        product_search = ProductSearch(barcode=barcode)
    except ValueError as e:
        logging.info(f"Invalid barcode: {barcode}, error: %s", e)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid barcode",
        )

    async with scraper:
        result = await scraper.scrape(product_search.barcode, strategy.BarcodeLookupStrategy())
        await repository.create(obj_in=result)

    return result.html
