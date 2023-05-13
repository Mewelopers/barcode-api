from typing import Any, Callable, Optional, Type, get_type_hints

from pydantic import BaseModel


def make_optional(
    include: Optional[list[str]] = None,
    exclude: Optional[list[str]] = None,
) -> Callable[[Type[BaseModel]], Type[BaseModel]]:
    """Return a decorator to make model fields optional"""

    # Create the decorator
    def decorator(cls: Type[BaseModel]) -> Type[BaseModel]:
        type_hints = get_type_hints(cls)
        fields: Any = cls.__fields__
        if include is None:
            fields = fields.items()
        else:
            # Create iterator for specified fields
            fields = ((name, fields[name]) for name in include if name in fields)
            # Fields in 'include' that are not in the model are simply ignored
        for name, field in fields:
            if exclude is not None and name in exclude:
                continue
            if not field.required:
                continue
            # Update pydantic ModelField to not required
            field.required = False
            # Update/append annotation
            cls.__annotations__[name] = Optional[type_hints[name]]
        return cls

    return decorator
