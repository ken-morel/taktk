"""\
Provides base class for taktk application creation
Copyright (C) 2022  ken-morel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from logging import getLogger
from pathlib import Path
from tempfile import NamedTemporaryFile
from types import ModuleType
from typing import Any, Optional
from pyoload import annotate
from ttkbootstrap import Window
from . import (
    ON_CREATE_HANDLERS,
    application_server,
    component,
    dictionary,
    media,
    menu,
    page,
    store,
)

log = getLogger(__name__)


@annotate
class Application:
    """
    Has optional attributes to specify behaviour including:

    - **dictionaries**: The path to the dictionnary directory taktk should
      fetch dictionaries from
    - **fallback_language**: The fallback language to use in case the locale's
      language could not be found in dictionaries
    - **params**: `dict[str,]`: Additional params to pass to ttkbootstrap
      Window on window
      creation.
    - **menu**: an optional `taktk.menu.Menu` object to use as toplevel menu
    - **layout**: an instance of `Layout` class you should define yourself
    """

    dictionaries: dictionary.Dictionaries = None
    fallback_language: str
    menu: Optional[menu.Menu]
    layout: Optional[component.Component]
    _store: Optional[store.Store] = None
    address: Optional[tuple[str, int]]
    icon: Optional[str | media.Image]
    _create_params: tuple[
        Optional[Path | str | dictionary.Dictionaries],
        dict[str, Any],
        tuple[None, dict] | store.Store,
        Optional[Path | str | media.Image],
        type(Window),
    ]
    media_path: Optional[str | Path]
    pages: ModuleType

    def __init__(
        self,
        pages: ModuleType,
        dictionaries: Optional[Path | str | dictionary.Dictionaries] = None,
        fallback_language: str = "english",
        params: dict[str, Any] = {},
        menu: Optional[menu.Menu] = None,
        layout: Optional[type] = None,
        store: tuple[None, dict] | store.Store = (None, {}),
        address: Optional[tuple[str, int]] = None,
        icon: Optional[str | media.Image] = None,
        media_path: Optional[str | Path] = None,
        window_class: type(Window) = Window,
    ):
        """
        Initialize the app and store most of the passed parameters into
        `._create_params`.

        :param dictionaries: The path to the application dictionaries directory
        or a `taktk.dictionary.Dictionary` instance.

        :param fallback_language: The fallback language to fetch from
        dictionary if locale's does not succeed.

        :param params: Additional parameters to pass to `window_class` on
        window creation.

        :param menu: The optional application menu, a `taktk.menu.Menu`
        instance

        :param layout: The application layout component instance to use.

        :param store: The path to application json _store_ database.

        :param address: The web address tuple for application server
        to listen at

        :param icon: The optional application icon spec or `taktk.media.Image`
        instance

        :param media_path: The optional path to global media directory

        :param window_class: The class to call on window creation.

        :param pages: The pages module
        """
        import taktk

        taktk.application = self

        self.menu = menu
        self.layout_class = layout
        self.layout = None
        self.address = address
        self.media_path = media_path
        self.pages = pages

        self.fallback_language = fallback_language
        self._create_params = (
            dictionaries,
            params,
            store,
            icon,
            window_class,
        )

    def init(self):
        """
        Subclass this method to initialize your app specific parameters
        """

    def set_language(self, lang: Optional[str] = None):
        """
        Installs the language passed as argument or the applications
        `.fallback_language`
        """
        self.dictionaries.get(
            language=lang, fallback_language=self.fallback_language
        ).install()

    def setup_taktk(self):
        """
        Internal to set up taktk components for app initialization
        """
        (
            dictionaries_path,
            _,
            _store,
            *__,
        ) = self._create_params
        if isinstance(_store, store.Store):
            self._store = _store
        elif isinstance(_store, tuple):
            _store, default = _store
            if _store is None:
                self._store_file = NamedTemporaryFile(delete=False)
                _store = self._store_file.name
            self._store = store.Store(_store, default=default)
        else:
            default = {}
            if _store is None:
                self._store_file = NamedTemporaryFile(delete=False)
                _store = self._store_file.name
            self._store = store.Store(_store, default=default)
        if dictionaries_path is not None:
            self.dictionaries = dictionary.Dictionaries(dictionaries_path)
            self.set_language()
        if self.media_path is not None:
            media.MEDIA_DIR = Path(self.media_path)

    def create(self):
        """
        Creates the app container
        """
        (
            _,
            params,
            __,
            icon,
            window_class,
        ) = self._create_params
        if icon is not None:
            if isinstance(icon, str):
                self.icon = media.get_image(icon)
                params["iconphoto"] = self.icon.full_path
            elif isinstance(icon, media.Image):
                self.icon = icon
                params["iconphoto"] = self.icon.full_path
            else:
                raise ValueError(
                    f"Wrong icon parameter {icon!r} was"
                    f" passed to {self.__class__.__name__}.__init__"
                )
        self.root = root = window_class(**params)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        if self.menu is not None:
            self.menu.toplevel(root)

        self.layout = self.layout_class()
        if self.layout is not None:
            self.layout.render(self.root)
            self.layout.container.grid(column=0, row=0, sticky="nsew")
            return self.layout["outlet"].outlet
        else:
            return root

    def run(self, entry: str = "/"):
        """
        Runs the app with the specified entry point.
        THe passed `entry` is set as first page
        """
        self.setup_taktk()
        root = self.create()
        self.init()
        for handler in ON_CREATE_HANDLERS:
            handler(self)
        if self.address is not None:
            self.listen_at(self.address)
        self.view = page.PageView(root, self.pages, self.get_store)
        self.view.geometry()
        self.view.url(entry)
        self.root.mainloop()

    def __call__(
        self,
        module: str,
        function: Optional[str] = None,
        redirect: bool = True,
        /,
        **params,
    ):
        """
        Refer to the app's view routing system with the specified params:

        :param module: The slash seperated path to the module
        :param function: optional handler name to call
        :param redirect: instructs the app to follow redirects
        :param params: Extra parameters passed to the handler
        """
        try:
            if "@" in module or "#" in module:
                raise ValueError(module, f"Did you mean app.url(...)?")
            self.view(module, function, params)
        except page.Redirect as e:
            target = e.url
            if redirect:
                self.view.url(target)
            else:
                raise
        self.layout.update()

    def url(self, url: str):
        """
        Targets the app to the specified url
        """
        return self.view.url(url)

    def exit(self):
        """
        Closes the app window.
        """
        self.root.destroy()

    def listen_at(self, address: tuple[str, int]):
        """
        starts a `taktk.application_server.ApplicationServer` at specified
        address
        """
        application_server.ApplicationServer(self, address).thread_serve()

    def redirect_to_singleton(self, url: str = "") -> bool:
        """
        Tries to query the apps address and:
        - if succeeds, sends a request to the instance with the passed url
        - if fails, starts an instance of the application

        :returns: A boolean telling if the app instance was started.
        """
        from urllib.request import urlopen

        try:
            urlopen(f"http://localhost:{self.address[1]}/!current").read()
        except Exception:
            self.run(url)
            return True
        else:
            urlopen(f"http://localhost:{self.address[1]}/" + url.lstrip("/"))
            return False

    def get_store(self) -> store.Store:
        """
        Returns the application store instance.
        """
        return self._store
