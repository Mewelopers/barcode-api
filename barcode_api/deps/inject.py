from barcode_api import services

from .ResolveService import ResolveService

jwt_service = ResolveService(services.JwtService)
