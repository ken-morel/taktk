from ttkbootstrap import Window
from .page import *
import json
from tempfile import NamedTemporaryFile
from .store import Store
from .media import get_media, get_image
from logging import getLogger
from . import ON_CREATE_HANDLERS

log = getLogger(__name__)


class Application:
    dictionaries = None
    fallback_language = "English"
    params = {}
    menu = None
    layout = None
    destroy_cache: int = 5
    store = (None, {})
    address = None
    icon = None

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
        if self.icon is not None:
            self.icon = get_image(self.icon)
            self.params['iconphoto'] = self.icon.full_path
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
        for handler in ON_CREATE_HANDLERS:
            handler(self)
        if self.address is not None:
            self.listen_at(self.address)
        self.view = PageView(root, self.pages, self, self.destroy_cache)
        self.view.geometry()
        self.view.url(entry)
        self.root.mainloop()

    def __call__(self, module, function=None, redirect=True, /, **params):
        try:
            self.view(module, function, params)
        except Redirect as e:
            target = e.url
            if redirect:
                self.view.url(target)
            else:
                raise
        self.layout.update()

    def url(self, url):
        return self.view.url(url)

    def exit(self):
        self.root.destroy()

    def listen_at(self, address):
        from .application_server import ApplicationServer
        ApplicationServer(self, address).thread_serve()

    def redirect_to_singleton(self, url=""):
        from urllib.request import urlopen
        try:
            urlopen(f"http://localhost:{self.address[1]}/!current")
        except Exception as e:
            self.run(url)
            return True
        else:
            urlopen(f"http://localhost:{self.address[1]}/" + url.lstrip('/'))
            return False
