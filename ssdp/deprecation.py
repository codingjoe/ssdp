import functools
import warnings


def moved(cls):
    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"'{__name__}.{cls.__qualname__}' has moved."
            f" Please import from: {cls.__module__}.{cls.__qualname__}",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return cls(*args, **kwargs)

    return wrapper
