from taktk.application import Application, Commander
from taktk.menu import Menu
from taktk.writeable import Writeable
from taktk.media import get_media
from taktk.component import Component
from . import pages
from pathlib import Path

DIR = Path(__file__).parent

recent_files = ['ama.py', 'test.py', 'ttkbootstrap.py', 'label.py']

def opener_file(file):
    def func():
        from taktk.notification import Notification
        Notification("Opener", "file open", bootstyle="info", duration=5000).show()
    return func


class Application(Application):
    commander = Commander(pages)
    dictionaries = DIR / "dictionaries"
    media = DIR / 'media'
    minsize = (400, 500)
    params = dict(
        themename="darkly",
    )
    menu = Menu({
        'file': {
            'open': lambda: None,
            'recent': {
                f: opener_file(f) for f in recent_files
            },
            '!sep': None,
            'quit': exit,
        },
        'preferences': {
            'language': [],
        },
        'quit': exit,
    })

    class NavBar(Component):
        r"""
        \frame padding=20 weight:y='1:10' weight:x='1:10'
            \button command={back} text=[nav.back] bootstyle='dark' pos:grid=0,0 pos:sticky='w'
            \button command={forward} text=[nav.next] bootstyle='dark' pos:grid=2,0 pos:sticky='w'
        """
        code = __doc__

        def __init__(self, app):
            self.app = app
            super().__init__()

        def back(self):
            self.app.back()

        def forward(self):
            self.app.forward()

    def create(self):
        from ttkbootstrap import Frame, Button

        container = super().create()
        root = self.root
        root.minsize(400, 500)
        nav = self.NavBar(self)
        nav.render(container).grid(column=0, row=0, sticky="nsew")
        frm = Frame(container)
        frm.grid(column=0, row=1)
        return frm

    def init(self):
        self.menu['preferences.language'] = {l: self.dictionaries.get(l).install for l in self.dictionaries.languages}

    def back(self):
        self.view.back()

    def forward(self):
        self.view.forward()
