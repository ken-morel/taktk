from importlib import import_module
from ttkbootstrap import Window


class Application:
    dictionaries = None
    fallback_language = 'English'
    params = {}
    menu = None
    layout = None
    destroy_cache: int = 5

    def __init__(self):
        import taktk

        taktk.application = self

    def init(self):
        pass

    def set_language(self, lang=None):
        self.dictionaries.get(language=lang, fallback_language=self.fallback_language).install()

    def setup_taktk(self):
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
            self.layout.render(root).grid(column=0, row=0, sticky='nsew')
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


class PageView:

    def __init__(self, parent, commander, app, destroy_cache: int = 5):
        self.history = []
        self.current_page = None
        self.parent = parent
        self.commander = commander
        self.current_widget = None
        self.app = app
        self.destroy_cache = destroy_cache

    def geometry(self):
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

    def url(self, url):
        result = self.commander.run_command(url)
        if result:
            self.view_component(result)

    def view_component(self, component):
        if self.current_page is None:
            self.current_page = 0
        else:
            self.current_page += 1
        current = self.current_widget
        self.history.insert(self.current_page, component)
        self.current_widget = component.render(self.parent)
        self.current_widget.grid(column=0, row=0, sticky="nsew")
        if current is not None:
            self.destroy_later(current)

    def destroy_later(self, widget, cache=[]):
        cache.append(widget)
        if len(cache) > self.destroy_cache:
            cache.pop(0).destroy()

    def back(self):
        if self.current_page > 0:
            self.focus_page(self.current_page - 1)

    def forward(self):
        if self.current_page < len(self.history) - 1:
            self.focus_page(self.current_page + 1)

    def focus_page(self, idx):
        page = self.history[idx]
        if self.current_widget is not None:
            self.current_widget.destroy()
        self.current_widget = self.history[idx].render(self.parent)
        self.current_widget.grid(column=0, row=0, sticky="nsew")
        self.current_page = idx


class Commander:
    def __init__(self, package):
        self.package = package

    def run_command(self, cmd):
        cmd = cmd.rstrip("/")
        path = [self.package.__package__] + list(filter(bool, cmd.split("/")))
        return import_module(".".join(path)).handle()
