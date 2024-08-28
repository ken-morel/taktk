from ttkbootstrap import Window
from .page import *
import json
from tempfile import NamedTemporaryFile
from .store import Store
from logging import getLogger

log = getLogger(__name__)


class Application:
    dictionaries = None
    fallback_language = "English"
    params = {}
    menu = None
    layout = None
    destroy_cache: int = 5
    store = (None, {})

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
        if isinstance(self.store, tuple):
            store, default = self.store
        else:
            store = self.store
            default = {}
        if store is None:
            self._store_file = NamedTemporaryFile(delete=False)
            store = self._store_file.name
        self.store = Store(store, default=default)
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
        root.columnconfigure(0, weight=10)
        root.rowconfigure(0, weight=10)
        if self.menu is not None:
            self.menu.toplevel(root)
        if self.Layout is not None:
            self.layout = self.Layout(self)
            self.layout.render(root).grid(column=0, row=0, sticky="nsew")
            return self.layout["outlet"].widget
        else:
            return root

    def run(self, entry="/"):
        self.setup_taktk()
        root = self.create()
        self.init()
        self.view = PageView(root, self.pages, self, self.destroy_cache)
        self.view.geometry()
        self.view.url(entry)
        self.root.mainloop()

    def __call__(self, module, function=None, /, **params):
        self.view(module, function, params)
        self.layout.update()

    def exit(self):
        self.root.destroy()
