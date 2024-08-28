from importlib import import_module
from urllib.parse import urlparse, parse_qsl
import json
import re
from decimal import Decimal
# ParseResult(scheme='http', netloc='192.168.23.48', path='/todos/sign.php', params='', query='reason=3', fragment='out')


class PageView:
    def __init__(self, parent, page, app, destroy_cache: int = 5):
        self.history = []
        self.current_page = None
        self.parent = parent
        self.current_widget = None
        self.app = app
        self.store = app.store
        self.destroy_cache = destroy_cache
        self.package = page

    def geometry(self):
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

    def url(self, url):
        target = url
        while target is not None:
            try:
                result = self.exec_url(target)
            except Redirect as r:
                target = r.url
            else:
                target = None

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

    def exec_url(self, cmd):
        parsed = urlparse(cmd)
        path = [self.package.__package__] + list(filter(bool, cmd.split("/")))
        args = {k: json.loads(v) for k, v in parse_qsl(parsed.query)}
        return self(parsed.path, parsed.fragment, args)

    def __call__(self, module, handler, params={}, /, **kwparams):
        from .component import Component
        if isinstance(module, str):
            module, urlparams = self.import_module(module)
        function = getattr(module, handler or 'handle')
        comp = None
        http = {'ok': True, 'error': None}
        page = function(
            self.store,
            *urlparams,
            **kwparams,
        )
        if page is None:
            return (None, None)
        elif isinstance(page, tuple):
            comp, http = page
        elif isinstance(page, Component):
            comp = page
        else:
            http = page
        if comp is not None:
            self.view_component(comp)
        return (comp, http)

    def import_module(self, path):
        module = self.package
        params = []
        for package in path.strip('/').split('/'):
            if not package.strip():
                continue
            try:
                module = import_module(module.__package__ + '.' + package)
            except ImportError:
                for regex, name, converter in URLPATTERNS:
                    if match := regex.fullmatch(package):
                        try:
                            module = import_module(module.__package__ + '.' + name)
                        except ImportError:
                            continue
                        else:
                            params.append(converter(package))
                            break
                else:
                    raise Error404(path)
        return module, params


class Error404(ValueError):
    pass


class Redirect(Exception):
    def __init__(self, url: str):
        self.url = url
        super().__init__()


URLPATTERNS = [
    (re.compile(r'^\d+$'), 'int', int),
    (re.compile(r'^\d+\.\d+$'), 'decimal', Decimal),
    (re.compile(r'.+'), 'str', str),
]


def register_urlpattern(regex, name=None, position=-2):
    def registerrer(func):
        if name is None:
            name = func.__name__.lower()
        if not isinstance(regex, re.Pattern):
            regex = re.compile(regex)
        URLPATTERNS.insert(position, (regex, '_' + name, converter))
