import itertools
from typing import Iterable, Any, Callable


class strategies:
    @staticmethod
    def integers(min_value: int = 0, max_value: int = 1) -> Iterable[int]:
        return range(min_value, max_value + 1)

    @staticmethod
    def just(value: Any) -> Iterable[Any]:
        return [value]


def given(
    *strategies: Iterable[Any],
) -> Callable[[Callable[..., Any]], Callable[..., None]]:
    def decorator(fn: Callable[..., Any]) -> Callable[..., None]:
        def wrapper(*args: Any, **kwargs: Any) -> None:
            for combo in itertools.product(*strategies):
                fn(*combo)

        return wrapper

    return decorator
