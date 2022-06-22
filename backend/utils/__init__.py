from typing import Optional, Any

from . import (
    date,
    iterables,
    module_interfacing,
    state_sharing,
    strings,
    time
)


def either_or(value: Optional[Any], default: Any) -> Any:
    """ Returns:
            value if != None, else default """

    return [value, default][value is None]
