from pathlib import Path

import yaml

from .writeable import Writeable, Subscribeable


class Dictionary(dict):
    subscribeable = Subscribeable()
    dictionary = None

    def __init__(self, data, language=None):
        super().__init__(data)
        self.language = language

    @classmethod
    def from_file(cls, path, language=None):
        with open(self.path) as f:
            return cls(yaml.safe_load(f.read()), language)

    def install(self):
        global dictionary
        dictionary = self
        Dictionary.dictionary = self
        import builtins

        builtins._ = self
        Dictionary.subscribeable.warn_subscribers()

    def __call__(self, path):
        obj = self
        try:
            for sub in path.split("."):
                obj = obj[sub]
        except KeyError as e:
            raise TranslationNotFound(path) from e
        return obj

    @classmethod
    def subscribe(cls, obj, method):
        cls.subscribeable.subscribe(obj, method)


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
            return Dictionary.from_file(
                self.languages[language], language=language
            )
        else:
            return Dictionary.from_file(
                self.languages[fallback_language], language=fallback_language
            )


class Translation(Writeable):
    def __init__(self, expr: str):
        """
        Creates the listener on the namespace with defined name
        """
        self.expr = expr
        Dictionary.subscribe(self, self.update)
        Writeable.__init__(self)

    def get(self):
        """
        Gets value from namespace
        """
        try:
            return dictionary(self.expr)
        except TypeError:
            return ":-("

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
