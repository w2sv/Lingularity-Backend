from typing import Set

from backend.utils.module_interfacing import abstractmoduleproperty


@abstractmoduleproperty()
def AVAILABLE_LANGUAGES() -> Set[str]:
    pass
