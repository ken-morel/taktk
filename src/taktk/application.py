from importlib import import_module
from ttkbootstrap import Window


class Application:
    dictionary = None
    params = {}

    def __init__(self):
        import taktk

        taktk.application = self

    def setup_dictionary(self):
        from .dictionary import Dictionary

        if self.dictionary is not None:
            Dictionary.from_directory(self.dictionary).install()

    def create(self):
        self.root = root = Window(**self.params)
        return root

    def run(self, entry="/"):
        self.setup_dictionary()
        root = self.create()
        self.view = PageView(root, self.commander)
        self.view.geometry()
        self.view.url(entry)
        self.root.mainloop()

    def __call__(self, url: str):
        self.view.url(url)


class PageView:
    def __init__(self, parent, commander):
        self.history = []
        self.current_page = None
        self.parent = parent
        self.commander = commander
        self.current_widget = None

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
        if self.current_widget is not None:
            self.current_widget.destroy()
        self.history.insert(self.current_page, component)
        self.current_widget = component.render(self.parent)
        self.current_widget.grid(column=0, row=0, sticky="nsew")

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
