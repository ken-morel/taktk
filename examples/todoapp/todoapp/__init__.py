from . import pages
from pathlib import Path
from taktk.application import Application
from taktk.component import Component
from taktk.component import Component
from taktk.media import get_media
from taktk.menu import Menu
from taktk.writeable import Writeable
from taktk.dictionary import Dictionary

from .admin import DIR, User, Todo
from taktk.notification import Notification

recent_files = ["ama.py", "test.py", "ttkbootstrap.py", "label.py"]


def opener_file(file):
    def func():
        from taktk.notification import Notification

        Notification(
            "Opener", "file open", bootstyle="info", duration=5000
        ).show()

    return func


class Application(Application):
    pages = pages
    dictionaries = DIR / "dictionaries"
    media = DIR / "media"
    params = dict(
        themename="darkly",
        minsize=(800, 400),
    )
    destroy_cache = 5
    menu = Menu(
        {
            "@file": {
                "@open": lambda: None,
                "@recent": {f: opener_file(f) for f in recent_files},
                "!sep": None,
                "@/menu.quit": exit,
            },
            "@preferences": {
                "@language": {},
            },
            "@quit": exit,
        },
        translations="menu",
    )
    store = (
        DIR / "store.json",
        {
            "language": "english",
        },
    )

    def init(self):
        self.menu["@preferences/@language"] = {
            l: self.dictionaries.get(l).install
            for l in self.dictionaries.languages
        }
        style = self.root.style
        self.menu["@preferences/@theme"] = {
            t: lambda s=self.set_theme, t=t: s(t) for t in style.theme_names()
        }
        try:
            self.root.style.theme_use(self.store['theme'])
        except Exception as e:
            log.error(e)
        self.menu.update()
        self.set_language(self.store["language"])
        Dictionary.subscribe(self.update_language)

    def set_theme(self, theme):
        self.root.style.theme_use(theme)
        self.store['theme'] = theme
        Notification(
            "Todos",
            _("preferences.success_modified"),
            bootstyle="info",
            duration=10000,
        ).show()

    def back(self):
        self.view.back()

    def forward(self):
        self.view.forward()

    def update_language(self):
        self.store["language"] = Dictionary.dictionary.language
        self.store.save()
        Notification(
            "Todos",
            _("preferences.success_modified"),
            bootstyle="info",
            duration=10000,
        ).show()

    class Layout(Component):
        r"""
        \frame weight:x='0: 10' weight:y='1: 10, 2: 10'
            \frame padding=5 weight:y='2:10' weight:x='2:10' pos:grid=0,0 pos:sticky='nsew'
                \button command={back}    image=img:@backward{width: 20} pos:grid=0,0 pos:sticky='w' bootstyle='dark outline'
                \label text={f'logged in as: {User.current().name}' if User.current() else "not logged in!"} pos:grid=1,0
                \button command={forward} image=img:@forward{width: 20}  pos:grid=3,0 pos:sticky='e' bootstyle='dark outline'
            \frame:outlet pos:grid=0,1
        """

        user = None

        def __init__(self, app):
            self.app = app
            super().__init__()

        def back(self):
            self.app.back()

        def forward(self):
            self.app.forward()

        User = User
