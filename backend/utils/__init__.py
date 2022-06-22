from typing import Any, Optional

from . import (
    date,
    iterables,
    module_interfacing,
    strings,
    time
)


def either_or(value: Optional[Any], default: Any) -> Any:
    """ Returns:
            value if != None, else default """

    return [value, default][value is None]
