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
from ..writeable import Writeable, resolve
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
        if "." in name:
            try:
                mod = self.package.__package__
            except AttributeError:
                raise ValueError(
                    f"{self.package} is not a package, does not have {name}"
                ) from None
            else:
                mod_path, name = name.rsplit(".", 1)
                mod = import_module(mod + "." + mod_path)
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
    widget = None

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
        self.raw_attrs = attrs

    def _position_(self):
        if "xweights" in self._pos_params_:
            for col, weight in self._pos_params_['xweights'].items():
                self.widget.columnconfigure(
                    col, weight=weight
                )
        if "yweights" in self._pos_params_:
            for row, weight in self._pos_params_['yweights'].items():
                self.widget.rowconfigure(
                    row, weight=weight
                )

        pos = self._pos_
        if pos is None:
            return
        match pos:
            case ("pack", _):
                self.widget.pack()
            case ("grid", coord):
                coord = resolve(coord)
                grid_params = ("sticky",)
                grid = {
                    k: v
                    for k, v in self._pos_params_.items()
                    if k in grid_params
                }
                if len(coord) == 2:
                    (x, y) = coord
                    grid["column"] = x
                    grid["row"] = y
                elif len(coord) == 4:
                    (x, y, xs, ys) = coord
                    grid["column"] = x
                    grid["row"] = y
                    grid["columnspan"] = xs
                    grid["rowspan"] = ys
                else:
                    raise ValueError("wrong grid tuple", coord)
                if "xweight" in self._pos_params_:
                    self.widget.master.columnconfigure(
                        x, weight=int(self._pos_params_["xweight"])
                    )
                if "yweight" in self._pos_params_:
                    self.widget.master.rowconfigure(
                        y, weight=int(self._pos_params_["yweight"])
                    )
                self.widget.grid(**grid)
            case wrong:
                raise ValueError("unrecognised position tuple:", wrong)

    def update(self):
        for child in self.children:
            child.update()

    def _update(self):
        if self.widget is None:
            return
        params = {
            **{
                self.conf_aliasses[k]: resolve(v)
                for k, v in vars(self.attrs).items()
                if k in self.conf_aliasses and v is not Nil
            }
        }
        self.widget.configure(**params)

    def make_bindings(self):
        for event, handler in self.event_binds.items():
            self.widget.bind(f"<{event}>", resolve(handler))

    def create(self):
        self.event_binds = {}
        vals = {}
        self._pos_params_ = {}
        for key, value in self.raw_attrs.items():
            if ":" in key:
                st, name = key.split(":", 1)
                if st == "bind":
                    self.event_binds[name] = parser.evaluate_literal(
                        value, self.namespace
                    )
                elif st == "pos":
                    if name == "grid":
                        self._pos_ = (
                            name,
                            parser.evaluate_literal(value, self.namespace),
                        )
                    else:
                        self._pos_params_[name] = parser.evaluate_literal(
                            value, self.namespace
                        )
                elif st == 'weight':
                    value = parser.evaluate_literal(
                        value, self.namespace
                    )
                    if name == 'x':
                        xweights = {}
                        for x in value.split(','):
                            i, w = map(lambda s: int(s.strip()), x.strip().split(':'))
                            xweights[i] = w
                        self._pos_params_['xweights'] = xweights
                    elif name == 'y':
                        yweights = {}
                        for x in value.split(','):
                            i, w = map(lambda s: int(s.strip()), x.strip().split(':'))
                            yweights[i] = w
                        self._pos_params_['yweights'] = yweights
                    else:
                        raise ValueError(f'Wrong weight direction: {name!r}, should be x or y')
                else:
                    raise ValueError(
                        f"Unrecognised special attribute type {st!r}"
                        f"in attribute {key!r}"
                    )
            else:
                vals[key] = parser.evaluate_literal(value, self.namespace)
        for val in vals.values():
            if isinstance(val, Writeable):
                val.subscribe(self._update)
        try:
            self.attrs = self.__class__.attrs(**vals)
        except TypeError as e:
            raise TypeError(
                f"error while binding arguments to {self.__class__!r}",
                e,
                self.attrs,
            ) from None


@annotate
class EnumComponent(_Component):
    def __init__(
        self,
        object,
        alias,
        namespace,
        parent: "Optional[_Component]" = None,
    ):
        self.children = []
        self.parent = parent
        self.namespace = namespace
        self.alias = alias
        self.object = object
        if parent is not None:
            self.parent.children.append(self)

    def create(self, parent=None):
        parent = parent or self.parent.widget
        self.render_parent = parent
        self.widgets = []
        for idx, val in enumerate(self.object.get()):
            aidx, aval = self.alias
            setattr(self.namespace, aidx, idx)
            setattr(self.namespace, aval, val)
            for child in self.children:
                elt = child.create(parent)
                self.widgets.append(
                    (child, elt),
                )
        if len(self.widgets) > 0:
            return tuple(zip(*self.widgets))[1]
        else:
            return []

    def update(self):
        widgets = self.widgets.copy()
        self.create(self.render_parent)
        try:
            self.render_parent.update()  # for smoother renderring
        except Exception:
            pass
        for component, widget in widgets:
            component.widget = None
            widget.destroy()
            del widget


@annotate
class Component(_Component):
    _component_: _Component = None
    code: str = r"\frame"

    @classmethod
    def __init_subclass__(cls):
        try:
            cls._component_ = execute(cls.code, cls, ModularNamespace(builtin))
        except:
            pass

    def init(self):
        pass

    @annotate
    def __getitem__(self, item: str):
        try:
            return getattr(self, item)
        except AttributeError:
            try:
                return globals()[item]
            except IndexError as e:
                raise IndexError(item) from e

    @annotate
    def __setitem__(self, item: str, value):
        setattr(self, item, value)
        self._watch_changes_()

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
        self._last_ = {
            k: v for k, v in vars(self).items() if not k.startswith("_")
        }
        self.init()
        if not self._component_:
            self._component_ = execute(
                self.code, self, ModularNamespace(builtin)
            )

    def render(self, master):
        return self._component_.create(master)

    def update(self):
        self._watch_changes_()
        self._component_.update()

    def _watch_changes_(self):
        state = {k: v for k, v in vars(self).items() if not k.startswith("_")}
        if state != self._last_:
            self._warn_subscribers_()
        self._last_ = state


from .instructions import execute
