from ttkbootstrap import Window
from .page import *
from . import settings


class Application:
    dictionaries = None
    fallback_language = "English"
    params = {}
    menu = None
    layout = None
    destroy_cache: int = 5
    settings = None

    def __init__(self):
        import taktk

        taktk.application = self

    def init(self):
        pass

    def set_language(self, lang=None):
        self.dictionaries.get(
            language=lang, fallback_language=self.fallback_language
        ).install()

    def setup_taktk(self):
        if self.settings is not None:
            settings.init(self.settings)
            self.settings = settings.settings()
        if self.dictionaries is not None:
            from .dictionary import Dictionaries

            self.dictionaries = Dictionaries(self.dictionaries)
            self.set_language()
        if self.media is not None:
            from pathlib import Path
            from . import media

            media.MEDIA_DIR = Path(self.media)

    def create(self):
        self.root = root = Window(**self.params)
        if self.menu is not None:
            self.menu.toplevel(root)
        if self.Layout is not None:
            self.layout = self.Layout(self)
            self.layout.render(root).grid(column=0, row=0, sticky="nsew")
            return self.layout.outlet.widget
        else:
            return root

    def run(self, entry="/"):
        self.setup_taktk()
        root = self.create()
        self.init()
        self.view = PageView(root, self.commander, self, self.destroy_cache)
        self.view.geometry()
        self.view.url(entry)
        self.root.mainloop()

    def __call__(self, url: str):
        self.view.url(url)

    def exit(self):
        self.root.destroy()
