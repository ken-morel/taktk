import yaml
from pathlib import Path
from .writeable import Writeable


class Dictionary(dict):
    subscribers = set()

    def __init__(self, path=None, locale=None):
        super().__init__()
        self.path = path
        self.locale = locale
        self.load()

    def load(self):
        with open(self.path) as f:
            super().update(yaml.safe_load(f.read()))

    def install(self):
        global dictionary
        dictionary = self
        Dictionary.dictionary = self
        import builtins

        builtins._ = self
        for subscriber in Dictionary.subscribers:
            subscriber()

    def __call__(self, path):
        obj = self
        for sub in path.split("."):
            obj = obj[sub]
        return obj

    @classmethod
    def from_directory(
        cls, path="dictionary", locale=None, fallback_locale="English"
    ):
        files = Path(path).glob("*.yml")
        langs = {p.stem: p for p in files}
        if locale is None:
            import locale as loc

            locale = loc.getlocale()[0].split("_", 1)[0]
        if locale in langs:
            return cls(langs[locale], locale=locale)
        else:
            return cls(langs[fallback_locale], locale=fallback_locale)

    @classmethod
    def subscribe(cls, method):
        cls.subscribers.add(method)


class Translation(Writeable):
    def __init__(self, expr: str):
        """
        Creates the listener on the namespace with defined name
        """
        self.expr = expr
        self.subscribers = set()
        Dictionary.subscribe(self.update)

    def get(self):
        """
        Gets value from namespace
        """
        return dictionary(self.expr)

    def set(self, val) -> None:
        """
        Sets value to namespace
        """
        pass

    def update(self) -> bool:
        self.warn_subscribers()


dictionary = None
