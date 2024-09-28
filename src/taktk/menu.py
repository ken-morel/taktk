"""Contain helper class for menu management."""
from logging import getLogger

from tkinter import Menu as tkMenu, Toplevel
from . import dictionary, writeable
from typing import Callable, Optional, Any

log = getLogger(__name__)
MenuStructure = dict[str, Callable | str | dict]


class Menu(writeable.Subscriber):
    """Create a menu structure to be shown as popup or binded to a toplevel."""

    menu = None
    menu_structure = None

    def __init__(
        self,
        structure: MenuStructure,
        translations: str = "menu",
    ):
        """
        Create the menu from structure using translation heading.

        :param structure: A dictionary containing menu structure, view docs.
        :param translations: The translation heading to load translations from.
        """
        writeable.Subscriber.__init__(self)
        self.subscribe_to(dictionary.Dictionary.subscribeable, self.update)
        self.structure = structure
        self.translations = translations
        self.created = False

    def create(self) -> tkMenu:
        """Create the tkinter.Menu instance."""
        menubar = tkMenu()
        Menu.build_submenus(menubar, self._eval_structure())
        self.menu = menubar
        self.menu_structure = self._eval_structure()
        self.created = True
        return menubar

    @classmethod
    def build_submenus(cls, menu: tkMenu, structure: MenuStructure):
        """Recursively build the corresponding structure into the menu."""
        from .dictionary import Translation
        from .writeable import Writeable

        for label, contents in structure.items():
            try:
                idx, name = label
            except ValueError:
                continue
            if isinstance(name, (Writeable, Translation)):
                name = name.get()
            if callable(contents):  # it is a command
                menu.add_command(label=name, command=contents, underline=idx)
            elif isinstance(contents, dict):  # a submenu
                submenu = tkMenu(menu)
                menu.add_cascade(menu=submenu, label=name, underline=idx)
                cls.build_submenus(submenu, contents)
            elif isinstance(contents, Writeable):
                val = contents.get()
                if isinstance(val, bool):
                    menu.add_checkbutton(
                        label=name, variable=contents.booleanvar, underline=idx
                    )
            elif name == "!sep":
                menu.add_separator()
            else:
                raise ValueError(
                    f"wrong menu dict field: {label!r}:{contents!r}",
                )

    def post(self, xpos: int | tuple[int], ypos: Optional[int] = None):
        """
        Popup the menu at specified location.

        either:
        - my_menu.post((x, y))
        - my_menu.post(x, y)
        """
        if isinstance(xpos, tuple):
            xpos, ypos = xpos
        if self.menu_structure != self._eval_structure():
            self.create()
        self.menu.post(xpos, ypos)

    def toplevel(self, root: Toplevel) -> Toplevel:
        """Set the menu as the toplevel's menu."""
        if self.menu_structure != self._eval_structure():
            self.create()
        root["menu"] = self.menu
        return root

    def __getitem__(self, item: str | tuple[str]):
        """
        Get a menu sub item.

        The item may be a tuple of menu labels or the path to menu label
        separated by slashes.
        """
        if isinstance(item, str):
            parts = item.split("/")
        else:
            parts = tuple(item)
        obj = self.structure
        for x in parts:
            obj = obj[x]
        return obj

    def __setitem__(self, item: str | tuple[str], val: Any):
        """
        Set a menu sub item.

        The item may be a tuple of menu labels or the path to menu label
        separated by slashes.
        """
        if isinstance(item, str):
            parts = item.split("/")
        else:
            parts = tuple(item)
        obj = self.structure
        *path, item = parts
        for x in path:
            if x in obj:
                obj = obj[x]
            else:
                no = {}
                obj[x] = no
                obj = no
        obj[item] = val
        self.update()
        return val

    def update(self):
        """Update the menu object."""
        if self.created:
            self.menu.delete(0, "end")
            self.build_submenus(self.menu, self._eval_structure())

    def _eval_structure(self):
        def build_sub(alias, structure):
            from builtins import _

            ret = {}
            for child_name, child_contents in structure.items():
                menu_trans = child_name
                if child_name.startswith("@"):  # alias translation
                    menu_trans = child_name[1:]
                    absolute = menu_trans.startswith("/")
                    if absolute:
                        menu_trans = menu_trans[1:]
                    try:
                        basename = (
                            menu_trans if absolute else f"{alias}.{menu_trans}"
                        )
                        try:
                            name = _(f"{basename}.__label__")
                        except NameError:
                            name = "Not Found"
                        except Exception:
                            name = _(basename)
                    except Exception:
                        name = "Not found"
                else:
                    name = child_name
                if "&" in name:
                    name = name.index("&"), name.replace("&", "")
                else:
                    name = (None, name)
                if isinstance(child_contents, dict):
                    ret[name] = build_sub(
                        alias + f".{menu_trans}", child_contents
                    )
                else:
                    ret[name] = child_contents
            return ret

        return build_sub(self.translations, self.structure)
