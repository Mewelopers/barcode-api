from barcode_api import services

from .ResolveService import ResolveService

user_crud = ResolveService(services.UserCRUD)
