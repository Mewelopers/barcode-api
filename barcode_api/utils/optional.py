from typing import Any, Callable, Optional, Type, get_type_hints, TypeVar

from pydantic import BaseModel

_T = TypeVar("_T", bound=BaseModel)


def make_optional(
    include: Optional[list[str]] = None,
    exclude: Optional[list[str]] = None,
) -> Callable[[Type[_T]], Type[_T]]:
    """
    Return a decorator that makes specified fields in a Pydantic model optional.

    Args:
        include (Optional[list[str]]): A list of field names to make optional. If None, all fields are included.
        exclude (Optional[list[str]]): A list of field names to exclude from being made optional.

    Returns:
        Callable[[Type[BaseModel]], Type[BaseModel]]: A decorator that makes specified fields optional.

    Example:
        from pydantic import BaseModel
        from pydantic_tools.optional import make_optional

        @make_optional(include=['field1', 'field2'])
        class MyModel(BaseModel):
            field1: str
            field2: int
            field3: float = 3.14

        # Now field1 and field2 are optional
        model = MyModel(field3=2.71)
    """

    # Create the decorator
    def decorator(cls: Type[_T]) -> Type[_T]:
        type_hints = get_type_hints(cls)
        fields: Any = cls.__fields__
        if include is None:
            _fields = fields.items()
        else:
            # Create iterator for specified fields
            _fields = ((name, fields[name]) for name in include if name in fields)
            # Fields in 'include' that are not in the model are simply ignored
        for name, field in _fields:
            if exclude is not None and name in exclude:
                continue
            if not field.required:
                continue
            # Update pydantic ModelField to not required
            field.required = False
            # Update/append annotation
            cls.__annotations__[name] = Optional[type_hints[name]]  # type: ignore
        return cls

    return decorator
