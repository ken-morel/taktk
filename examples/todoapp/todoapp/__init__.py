from . import pages
from pathlib import Path
from taktk.application import Application
from taktk.application import Commander
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
    commander = Commander(pages)
    dictionaries = DIR / "dictionaries"
    media = DIR / "media"
    minsize = (400, 500)
    params = dict(
        themename="darkly",
    )
    destroy_cache = 1
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
    settings = (DIR / "settings.json", {
        "language": "english",
    })

    def init(self):
        self.menu["@preferences/@language"] = {
            l: self.dictionaries.get(l).install
            for l in self.dictionaries.languages
        }
        self.menu.update()
        self.set_language(self.settings['language'])
        Dictionary.subscribe(self.update_language)

    def back(self):
        self.view.back()

    def forward(self):
        self.view.forward()

    def update_language(self):
        self.settings['language'] = Dictionary.dictionary.language
        self.settings.save()
        Notification("Todos", _("preferences.success_modified"), bootstyle="info", duration=10000).show()

    class Layout(Component):
        r"""
        \frame
            \frame padding=5 weight:y='2:10' weight:x='2:10' pos:grid=0,0 pos:sticky='nsew'
                \button command={back}    image=img:@backward{width: 20} pos:grid=0,0 pos:sticky='w' bootstyle='dark outline'
                !if User.is_login()
                    \label text={f'logged in as {User.current().name}'} pos:grid=1,0
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
