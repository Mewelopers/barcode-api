import io
from uuid import uuid4

import numpy as np
from PIL import Image
from faker import Faker
from faker.providers import barcode

from barcode_api.schemas.token import OIDCToken
from barcode_api.schemas.auth import AuthRole, AuthScopes
from barcode_api.models.product import Product
from barcode_api.models.image_data import ImageData
from .types import MockImage

fake = Faker()
fake.add_provider(barcode)


def random_image(*, width: int, height: int) -> MockImage:
    data = np.random.randint(0, 256, size=width * height * 3, dtype=np.uint8)
    data = data.reshape((width, height, 3))
    image = Image.fromarray(data, "RGB")

    with io.BytesIO() as output:
        image.save(output, format="JPEG")
        return MockImage(size=(width, height), data=output.getvalue(), content_type="image/jpeg")


def build_oidc_token(
    roles: set[AuthRole] = {AuthRole.CLIENT},
    scopes: set[AuthScopes] = {
        AuthScopes.OFFLINE_ACCESS,
        AuthScopes.OPENID,
        AuthScopes.PROFILE,
        AuthScopes.JKP_API,
        AuthScopes.EMAIL,
        AuthScopes.ROLES,
    },
) -> OIDCToken:
    return OIDCToken(
        iss="test-iss",
        sub=f"{uuid4()}",
        aud="test-aud",
        exp=99999999999,
        iat=11111111111,
        role=roles,
        email="test-email@example.com",
        name="test-name",
        scope=scopes,
    )


def random_product() -> Product:
    return Product(
        name=f"{fake.word()} {fake.word()}-{uuid4()}",
        description=fake.text(),
        manufacturer=fake.company(),
        barcode=fake.ean(length=13),
        thumbnail=ImageData(data=random_image(width=100, height=100).data, id=uuid4()),
    )
