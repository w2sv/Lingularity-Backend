from typing import Callable, Iterator, Any, Optional


def return_value_capturing_generator(generator: Callable[..., Iterator[Any]]):
    class WrappedGenerator:
        def __init__(self, *args, **kwargs):
            self.generator: Iterator[Any] = generator(*args, **kwargs)
            self.return_value: Optional[Any] = None

        def __iter__(self):
            self.return_value = yield from self.generator

    return WrappedGenerator
