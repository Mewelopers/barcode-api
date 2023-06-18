import io

import numpy as np
from PIL import Image

from .types import MockImage


def random_image(*, width: int, height: int) -> MockImage:
    data = np.random.randint(0, 256, size=width * height * 3, dtype=np.uint8)
    data = data.reshape((width, height, 3))
    image = Image.fromarray(data, "RGB")

    with io.BytesIO() as output:
        image.save(output, format="JPEG")
        return MockImage(size=(width, height), data=output.getvalue(), content_type="image/jpeg")
