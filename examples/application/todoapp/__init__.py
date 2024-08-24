from taktk.application import Application, Commander
from . import pages
from pathlib import Path

DIR = Path(__file__).parent


class Application(Application):
    commander = Commander(pages)
    dictionary = DIR / "dictionary"
    minsize = (400, 500)
    params = dict(
        themename="darkly",
    )

    def create(self):
        from ttkbootstrap import Frame, Button

        container = super().create()
        root = self.root
        root.minsize(400, 500)
        nav = Frame(container)
        nav.grid(column=0, row=0, sticky="nsew")
        back = Button(nav, command=self.back, text="< back", bootstyle='dark')
        back.grid(column=0, row=0, sticky="w")
        back = Button(nav, command=self.forward, text="forward >", bootstyle='dark')
        back.grid(column=2, row=0, sticky="e")
        nav.columnconfigure(1, weight=10)
        frm = Frame(container)
        frm.grid(column=0, row=1)
        return frm

    def back(self):
        self.view.back()

    def forward(self):
        self.view.forward()
