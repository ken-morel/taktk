import yaml
from pathlib import Path


class Dictionary(dict):
    def __init__(self, path, locale=None):
        super().__init__()
        self.path = path
        self.locale = locale

    def load(self):
        with open(self.path) as f:
            super().update(yaml.safe_load(f.read()))

    def install(self):
        global dictionary
        dictionary = self
        import builtins
        builtins._ = self

    def __call__(self, path):
        obj = self
        for sub in path.split('.'):
            obj = obj[sub]
        return obj

    @classmethod
    def from_directory(cls, path='dictionary', locale=None, fallback_locale='English'):
        files = Path(path).glob("*.yml")
        print(tuple(Path('.').glob('*')), Path(path).exists())
        langs = {p.stem: p for p in files}
        print(langs)
        if locale is None:
            import locale as loc
            locale = loc.getlocale()[0].split("_", 1)[0]
        if locale in langs:
            return cls(langs[locale])
        else:
            return cls(langs[fallback_locale])

dictionary = None
