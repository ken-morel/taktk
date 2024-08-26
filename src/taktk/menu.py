from ttkbootstrap import Menu as ttkMenu


class Menu:
    menu = None
    menu_structure = None

    def __init__(self, structure):
        from .dictionary import Dictionary
        Dictionary.subscribe(self.update)
        self.structure = structure
        self._last = structure.copy()

    def create(self):
        menubar = ttkMenu()
        Menu.build_submenus(menubar, self.structure)
        self.menu = menubar
        self.menu_structure = self.structure.copy()
        return menubar

    @classmethod
    def build_submenus(cls, menu, structure):
        from .writeable import Writeable
        from .dictionary import Translation
        for name, contents in structure.items():
            if isinstance(name, Translation):
                name = name.get()
            if callable(contents):  # it is a command
                menu.add_command(label=name, command=contents)
            elif isinstance(contents, dict):  # a submenu
                submenu = ttkMenu(menu)
                menu.add_cascade(menu=submenu, label=name)
                cls.build_submenus(submenu, contents)
            elif isinstance(contents, Writeable):
                val = contents.get()
                if isinstance(val, bool):
                    menu.add_checkbutton(label=name, variable=contents.booleanvar)
            elif name == '!sep':
                menu.add_separator()

    def post(self, xpos, ypos):
        if not self.menu_structure == self.structure:
            self.create()
        self.menu.post(xpos, ypos)

    def toplevel(self, root):
        if not self.menu_structure == self.structure:
            self.create()
        root['menu'] = self.menu

    def __getitem__(self, item):
        obj = self.structure
        for x in item.split('.'):
            obj = obj[x]
        return obj

    def __setitem__(self, item, val):
        obj = self.structure
        *path, item = item.split('.')
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
        for k in self._last:
            self.menu.delete(k)
        self.build_submenus(self.menu, self.structure)
