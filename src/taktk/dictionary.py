import yaml
from pathlib import Path
from .writeable import Writeable


class Dictionary(dict):
    subscribers = set()

    def __init__(self, path, language=None):
        super().__init__()
        self.path = path
        self.language = language
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
        for subscriber in tuple(Dictionary.subscribers):
            try:
                subscriber()
            except:
                pass

    def __call__(self, path):
        obj = self
        for sub in path.split("."):
            obj = obj[sub]
        return obj

    @classmethod
    def subscribe(cls, method):
        cls.subscribers.add(method)


class Dictionaries:
    def __init__(self, path="dictionaries"):
        self.path = path
        self.languages = {p.stem: p for p in path.glob("*.yml")}

    def get(self, language=None, fallback_language="English"):
        if language is None:
            import locale as loc

            language = loc.getlocale()[0].split("_", 1)[0]
        if language in self.languages:
            return Dictionary(self.languages[language], language=language)
        else:
            return Dictionary(
                self.languages[fallback_language], language=fallback_language
            )


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
