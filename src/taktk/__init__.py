__version__ = "0.1.0a1"
__author__ = "ken-morel"


class NilType:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return "Nil"

    def __reduce__(self):
        return (self.__class__, ())

    def __bool__(self):
        return False

    def __instancecheck__(self, other):
        return other is Nil

    def __sub__(self, other):
        return other is Nil

    def __rsub__(self, other):
        return other is Nil


Nil = NilType()


def resolve(value):
    from .media import Resource, Image
    from .writeable import Writeable

    if isinstance(value, Resource | Writeable):
        return value.get()
    else:
        return value


ON_CREATE_HANDLERS = set()


def on_create(func):
    ON_CREATE_HANDLERS.add(func)
