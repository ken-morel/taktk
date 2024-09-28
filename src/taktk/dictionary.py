from pathlib import Path

import yaml
import builtins
from . import writeable
from typing import Optional, Callable


class Dictionary(dict):
    """Creates or loads a dictionary."""

    subscribeable = writeable.Subscribeable()
    dictionary = None

    def __init__(self, data: dict, language: Optional[str] = None):
        """Create a menu from dictionary and optional language name."""
        super().__init__(data)
        self.language = language

    @classmethod
    def from_file(
        cls, path: str, language: Optional[str] = None
    ) -> "Dictionary":
        """Create a dictionary from filename and optional language name."""
        with open(path) as f:
            return cls(yaml.safe_load(f.read()), language)

    def install(self, install_builtins: bool = True):
        """Install dictionary for usage by taktk."""
        global dictionary
        dictionary = self
        Dictionary.dictionary = self
        if install_builtins:
            builtins._ = self
        Dictionary.subscribeable.warn_subscribers()

    def __call__(self, path: str) -> str | dict:
        """Get a dictionary item specified by path."""
        obj = self
        try:
            for sub in path.split("."):
                obj = obj[sub]
        except KeyError as e:
            raise TranslationNotFound(path) from e
        return obj

    @classmethod
    def subscribe(cls, obj: writeable.Subscriber, method: Callable):
        """Subscribe the subscriber to dictionary changes."""
        cls.subscribeable.subscribe(obj, method)


class Dictionaries:
    """Holds a mapping of dictionaries to languages."""

    def __init__(self, path: str = "dictionaries"):
        """Initialize the dictionaries from dictionaries folder path."""
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


class Translation(writeable.Writeable):
    def __init__(self, expr: str):
        """
        Creates the listener on the namespace with defined name
        """
        self.expr = expr
        Dictionary.subscribe(self, self.update)
        writeable.Writeable.__init__(self)

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
