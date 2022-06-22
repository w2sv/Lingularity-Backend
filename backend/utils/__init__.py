from typing import Any, Optional

from . import (
    date,
    iterables,
    strings,
    time
)


def either_or(value: Optional[Any], fallback: Any) -> Any:
    """ Returns:
            value if != None, else fallback """

    return [value, fallback][value is None]
