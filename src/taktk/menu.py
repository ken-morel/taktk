"""Class to manage tk menu."""
from .component import TkComponent

from efus.subscribe import Subscriber
from pyoload import annotate
from ttkbootstrap import Menu as ttkMenu
from typing import Any
from typing import Optional


@annotate
class Menu:
    """Taktk tk menu interface class."""

    menu: Optional[ttkMenu] = None
    menu_structure: Optional[dict] = None
    subscriber: Subscriber

    def __init__(self, structure: dict, translations: Optional[str] = None):
        """Create a taltl tk menu."""
        from .dictionary import Dictionary

        self.subscriber = Subscriber()
        self.subscribe.subscribe_to(Dictionary)
        self.structure = structure
        self.translations = translations

    def render(self):
        """Render the menu to tk menu."""
        menubar = ttkMenu()
        Menu._build_submenus(menubar, self._eval_structure())
        self.menu = menubar
        self.menu_structure = self._eval_structure()
        return menubar

    @classmethod
    def _build_submenus(cls, menu, structure):
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
                submenu = ttkMenu(menu)
                menu.add_cascade(menu=submenu, label=name, underline=idx)
                cls._build_submenus(submenu, contents)
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

    @annotate
    def post(self, xpos: int, ypos: int):
        """Post the menu at xpos and ypos."""
        if self.menu_structure != self._eval_structure():
            self.create()
        self.menu.post(xpos, ypos)

    def toplevel(self, root: Any):
        """Attach the menu to the specified toplevel."""
        if self.menu_structure != self._eval_structure():
            self.create()
        root["menu"] = self.menu

    def __getitem__(self, item: str):
        obj = self.structure
        for x in item.split("/"):
            obj = obj[x]
        return obj

    def __setitem__(self, item, val):
        obj = self.structure
        *path, item = item.split("/")
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
        """Update the tkinter menu."""
        self.menu.delete(0, "end")
        self._build_submenus(self.menu, self._eval_structure())

    def _eval_structure(self):
        def build_sub(alias, structure):
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
                        except:
                            name = _(basename)
                    except:
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
