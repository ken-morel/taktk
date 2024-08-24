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
from ..writeable import Writeable
from .. import Nil


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
        for val in vals.values():
            if isinstance(val, Writeable):
                val.subscribe(self._update)
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

    def update(self):
        for child in self.children:
            child.update()

    def _update(self):
        same = [x for x in dir(self.__class__.attrs) if not x.startswith('_')]
        param_names = {
            **dict(zip(same, same)),
        }
        params = {
            **{
                param_names[k]: v for k, v in vars(self.attrs).items() if k in param_names and v is not Nil
            }
        }
        for param, val in params.items():
            if isinstance(val, Writeable):
                val = val.get()
            self.widget[param] = val


@annotate
class Component(_Component):
    _component_: _Component = None
    code: str = r"\frame"

    def __getitem__(self, item: str):
        return getattr(self, item)

    def __setitem__(self, item: str, value):
        setattr(self, item, value)
        self._warn_subscribers_()

    def _subscribe_(self, subscriber):
        self._subscribers_.add(subscriber)

    def _unsubscribe_(self, subscriber):
        self._subscribers_.remove(subscriber)

    def _warn_subscribers_(self):
        for subscriber in self._subscribers_:
            subscriber()

    def __init__(self, parent: "Optional[object]" = None):
        from . import builtin

        self._parent_ = parent
        self._subscribers_ = set()

        self._component_ = execute(
            self.code, self, ModularNamespace(builtin)
        )

    def render(self, master):
        return self._component_.create(master)

    def update(self):
        self._component_.update()


from .instructions import execute
