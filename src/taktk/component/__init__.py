"""
The main components tool

Copyright (C) 2024  ken-morel

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

from types import ModuleType
from pyoload import annotate
from importlib import import_module
from typing import Optional
from dataclasses import dataclass


class ComponentNamespace:
    """
    Stores the namespace from which _component names will be loaded
    """


class ModularNamespace(ComponentNamespace):
    """
    Creates a modular namespace based on a module path
    """

    package: ModuleType

    @annotate
    def __init__(self, package: ModuleType):
        """
        Initializes the namespace with the gicen module.
        """
        self.package = package

    def __getitem__(self, name: str):
        if '.' in name:
            try:
                mod = self.package.__package__
            except AttributeError:
                raise ValueError(f"{self.package} is not a package, does not have {name}") from None
            else:
                mod_path, name = name.rsplit('.', 1)
                mod = import_module(mod + '.' + mod_path)
        else:
            mod = self.package
        try:
            if hasattr(mod, name):
                _component = getattr(mod, name)
            else:
                raise NameError(f"{name} not in module {mod}")
        except AssertionError:
            pass
        else:
            return _component


class _Component:
    parent: "Optional[_Component]"
    children: "list[_Component]"
    _pos_ = None

    @classmethod
    def __init_subclass__(cls):
        if not hasattr(cls, "attrs"):
            cls.attrs = type("attrs", (object,), {})
        cls.attrs = dataclass(cls.attrs)

    def __init__(
        self,
        parent: "Optional[_Component]" = None,
        attrs: dict[str] = {},
        namespace: dict[str] = {},
    ):
        self.children = []
        self.parent = parent
        self.namespace = namespace
        if parent is not None:
            self.parent.children.append(self)
        vals = {}
        for key, value in attrs.items():
            if ":" in key:
                st, name = key.split(":", 1)
                if st == "on":
                    raise NotImplementedError("events not yet implemented")
                elif st == "pos":
                    if name == "grid":
                        self._pos_ = (
                            name,
                            parser.evaluate_literal(value, namespace),
                        )
                    else:
                        raise NotImplementedError(
                            f"unemplemented {name!r} positioning"
                        )
                else:
                    raise ValueError(
                        f"Unrecognised special attribute type {st!r}"
                        f"in attribute {key!r}"
                    )
            else:
                vals[key] = parser.evaluate_literal(value, namespace)
        try:
            self.attrs = self.__class__.attrs(**vals)
        except TypeError as e:
            raise TypeError(
                f"error while binding arguments to {self.__class__!r}",
                e,
                attrs,
            ) from None

    def _position_(self):
        if self._pos_ is None:
            return
        match self._pos_:
            case ("pack", _):
                self.widget.pack()
            case ("grid", (x, y)):
                self.widget.grid(column=x, row=y)
            case wrong:
                raise ValueError("unrecognised position tuple:", wrong)


@annotate
class Component(_Component):
    __component__: _Component = None
    code: str = r"\frame"

    def __getitem__(self, item: str):
        return getattr(self, item)

    def __setitem__(self, item: str, value):
        return setattr(self, item, value)

    def __init__(self, parent: "Optional[object]" = None):
        from . import builtin

        self.__component__ = execute(
            self.code, self, ModularNamespace(builtin)
        )
        self.__parent__ = parent

    def render(self, master):
        return self.__component__.create(master)


from .instructions import execute
