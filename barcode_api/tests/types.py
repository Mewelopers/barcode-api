from dataclasses import dataclass


@dataclass
class MockImage:
    size: tuple[int, int]
    data: bytes
    content_type: str
