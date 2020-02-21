from typing import Any, Callable


class cached_property:
    """Decorator that converts a method with a single self argument into a property cached on the instance."""
    name: str = None

    def __init__(self, func: Callable):
        self.func, self.__doc__ = func, func.__doc__

    def __set_name__(self, owner: Any, name: str):
        if self.name is None:
            self.name = name

    def __get__(self, instance: Any, cls: Any = None) -> Any:
        """
        Call the function and put the return value in instance.__dict__ so that
        subsequent attribute access on the instance returns the cached value
        instead of calling cached_property.__get__().
        """
        if instance is None:
            return self
        else:
            setattr(instance, self.name, (ret := self.func(instance)))
            # ret = instance.__dict__[self.name] = self.func(instance)
            return ret
