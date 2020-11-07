from typing import List, Optional, Callable, Any, Iterator, Tuple
import sys
from functools import partial
from types import ModuleType


def abstractmodulemethod(ignore_modules: Optional[List[str]] = None):
    """ Decorator enforcing implementation of passed abstractmethod in all modules
        located within package from whose __init__ the decorator was invoked, except
        the ones specified in ignore_modules

        Checks whether variable of same name as abstractmethod in module is callable,
        however not whether the signatures of abstractmethod and implementation match """

    def wrapper(abstractmethod: Callable):
        calling_module = _origin_module(abstractmethod)

        for module_name, module in _module_item_iterator(calling_module, ignore_modules):
            if abstractmethod.__name__ not in dir(module) or not _abstractmethod_implementation_callable(abstractmethod, module):
                raise NotImplementedError(f"Can't initialize {calling_module}.{module_name} with abstractmodulemethod {abstractmethod.__name__}")

    return wrapper


def abstractmoduleproperty(ignore_modules: Optional[List[str]] = None):
    def wrapper(abstractproperty: Callable):
        calling_module = _origin_module(abstractproperty)

        for module_name, module in _module_item_iterator(calling_module, ignore_modules):
            if abstractproperty.__name__ not in dir(module):
                raise NotImplementedError(
                    f"Can't initialize {calling_module}.{module_name} with abstractmoduleproperty {abstractproperty.__name__}")

    return wrapper


def _origin_module(variable: Any) -> ModuleType:
    return sys.modules[variable.__module__]


def _module_item_iterator(calling_module: ModuleType, ignore_modules: Optional[List[str]]) -> Iterator[Tuple[str, ModuleType]]:
    __is_package_module = partial(
        _is_package_module,
        package_name=calling_module.__package__,
        ignore_modules=ignore_modules or []
    )

    return filter(lambda item: __is_package_module(*item), calling_module.__dict__.items())


def _is_package_module(module_name: str, module: ModuleType, package_name: str, ignore_modules: List[str]) -> bool:
    return module_name not in ignore_modules and _is_module(module) and module.__package__ == package_name


def _is_module(module_candidate: object) -> bool:
    return module_candidate.__class__.__name__ == 'module'


def _abstractmethod_implementation_callable(abstractmethod: Callable, module: ModuleType) -> bool:
    return hasattr(module.__dict__[abstractmethod.__name__], '__call__')

