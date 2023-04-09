from typing import Type, TypeVar

from barcode_api.services import mixin
from fastapi import Depends

from .common import Session, Settings, get_db, get_settings

service_type = TypeVar("service_type", bound=mixin.AppService | mixin.AppCrudService)


class ResolveService:
    def __init__(self, service: Type[service_type]) -> None:
        self.service = service

    def __call__(
        self, db: Session = Depends(get_db), config: Settings = Depends(get_settings)
    ) -> Type[service_type]:
        if type(self.service) is mixin.AppCrudService:
            raise TypeError("ResolveService can't be used with AppCrudService")
        return self.service(db=db, config=config)  # type: ignore
