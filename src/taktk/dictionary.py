from pathlib import Path

import yaml

from .writeable import Writeable


class Dictionary(dict):
    subscribers = set()
    dictionary = None

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
        try:
            for sub in path.split("."):
                obj = obj[sub]
        except KeyError as e:
            raise TranslationNotFound(path) from e
        return obj

    @classmethod
    def subscribe(cls, method):
        cls.subscribers.add(method)


class Dictionaries:
    def __init__(self, path="dictionaries"):
        self.path = path
        self.languages = (
            {p.stem.lower(): p for p in path.glob("*.yml")}
            | {p.stem.lower(): p for p in path.glob("*.yaml")}
            | {p.stem.lower(): p for p in path.glob("*.dictionary")}
        )

    def get(self, language=None, fallback_language="english"):
        if language is None:
            import locale as loc

            language = loc.getlocale()[0].split("_", 1)[0]
        language = language.lower()
        fallback_language = fallback_language.lower()
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


class TranslationNotFound(ValueError):
    pass

dictionary = None
