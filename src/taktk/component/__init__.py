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

from dataclasses import dataclass
from importlib import import_module
from types import ModuleType
from typing import Optional

from pyoload import annotate

from .. import Nil
from ..writeable import Writeable
from .. import resolve


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


@annotate
class _Component:
    parent = None
    children: list
    _pos_ = None
    container = None
    outlet = None
    _aligner = None

    def _init_subclass(cls):
        if not hasattr(cls, "Attrs"):
            cls.Attrs = type("Attrs", (object,), {})
        cls.Attrs = dataclass(cls.Attrs)

    __init_subclass__ = _init_subclass

    def __init__(
        self,
        namespace: "Namespace",
        parent = None,
        attrs: dict[str] = {},
    ):
        self.children = []
        self.parent = parent
        self.namespace = namespace
        if parent is not None:
            self.parent.children.append(self)
        self.raw_attrs = attrs

    def _align_widget(self, widget, params):
        if self._children_align == 'r':
            widget.grid(column=self._align_offset, row=0, **params)
        elif self._children_align == 'c':
            widget.grid(row=self._align_offset, column=0, **params)
        else:
            raise ValueError("unknown align offset:", self._children_align)
        self._align_offset += 1

    def _position_(self):
        grid_params = ("sticky",)
        grid = {
            k: v
            for k, v in self._pos_params_.items()
            if k in grid_params
        }
        if "xweights" in self._pos_params_:
            for col, weight in self._pos_params_["xweights"].items():
                self.container.columnconfigure(col, weight=weight)
        if "yweights" in self._pos_params_:
            for row, weight in self._pos_params_["yweights"].items():
                self.container.rowconfigure(row, weight=weight)

        if "align" in self._pos_params_:
            full_direction = self._pos_params_['align']
            self._align_offset = 0
            assert len(full_direction) > 0, "invalid empty direction in align"
            direction = full_direction[0]
            assert direction in "rc", "invalid direction"
            self._children_align = direction
            for child in self.children:
                child._aligner = self
        if self._aligner is not None:
            return self._aligner._align_widget(self.container, grid)
        pos = self._pos_
        if pos is None:
            return
        match pos:
            case ("pack", _):
                self.container.pack()
            case ("grid", coord):
                coord = resolve(coord)
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
                    self.container.master.columnconfigure(
                        x, weight=int(self._pos_params_["xweight"])
                    )
                if "yweight" in self._pos_params_:
                    self.container.master.rowconfigure(
                        y, weight=int(self._pos_params_["yweight"])
                    )
                self.container.grid(**grid)
            case wrong:
                raise ValueError("unrecognised position tuple:", wrong)

    def update(self):
        for child in self.children:
            child.update()

    def _update(self):
        pass

    def make_bindings(self):
        for event, handler in self.event_binds.items():
            self.container.bind(f"<{event}>", resolve(handler))

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
                    if name in ("grid",):
                        self._pos_ = (
                            name,
                            parser.evaluate_literal(value, self.namespace),
                        )
                    else:
                        self._pos_params_[name] = parser.evaluate_literal(
                            value, self.namespace
                        )
                elif st == "weight":
                    value = parser.evaluate_literal(value, self.namespace)
                    if name == "x":
                        xweights = {}
                        for x in value.split(","):
                            i, w = map(
                                lambda s: int(s.strip()), x.strip().split(":")
                            )
                            xweights[i] = w
                        self._pos_params_["xweights"] = xweights
                    elif name == "y":
                        yweights = {}
                        for x in value.split(","):
                            i, w = map(
                                lambda s: int(s.strip()), x.strip().split(":")
                            )
                            yweights[i] = w
                        self._pos_params_["yweights"] = yweights
                    else:
                        raise ValueError(
                            f"Wrong weight direction: {name!r}, should be x or y"
                        )
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
            self.attrs = self.__class__.Attrs(**vals)
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
        namespace,
        alias: tuple[str, str],
        parent: "Optional[_Component]" = None,
        instructions: list = [],
        component_space=None,
    ):
        self.children = []
        self.parent = parent
        self.parent_namespace = namespace
        self.object = object
        self.instructions = instructions  # instructions
        self.alias = alias
        self.component_space = component_space
        if parent is not None:
            self.parent.children.append(self)

    def create(self, parent=None):
        parent = parent or self.parent.outlet
        self.render_parent = parent
        self.widgets = []
        for idx, val in enumerate(self.object.get()):
            aidx, aval = self.alias
            namespace = Namespace(parents=[self.parent_namespace])
            namespace[aidx] = idx
            namespace[aval] = val
            for instr in self.instructions:
                comp = instr._eval(namespace, self.component_space)
                comp.create(parent)
                elt = comp.container
                self.widgets.append(
                    (comp, elt),
                )

    def update(self):
        widgets = self.widgets.copy()
        self.create(self.render_parent)
        try:
            self.render_parent.update()  # for smoother renderring
        except Exception:
            pass
        for component, widget in widgets:
            component.container = component.outlet = None
            widget.destroy()
            del widget


@annotate
class IfComponent(_Component):
    def __init__(
        self,
        condition,
        namespace,
        parent: "Optional[_Component]" = None,
        instructions: list = [],
        component_space=None,
    ):
        self.children = []
        self.parent = parent
        self.namespace = namespace
        self.condition = condition
        self.instructions = instructions  # instructions
        self.component_space = component_space
        if parent is not None:
            self.parent.children.append(self)

    def create(self, parent=None):
        parent = parent or self.parent.outlet
        self.render_parent = parent
        self.widgets = []
        self.condition.subscribe(self._update)
        if self.condition.get():
            for instr in self.instructions:
                comp = instr._eval(self.namespace, self.component_space)
                comp.create(parent)
                self.widgets.append(
                    (comp.container, comp.container),
                )

    def update(self):
        super().update()
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


from .instructions import Instruction
from .instructions import Namespace
from .instructions import execute


@annotate
class Component(_Component):
    _component_: _Component = None
    _instructions_: Instruction = None
    _code_: str = None

    def init(self):
        pass

    @annotate
    def __getitem__(self, item: str):
        try:
            return self.namespace[item]
        except AttributeError:
            try:
                return globals()[item]
            except IndexError as e:
                raise IndexError(item) from e

    @annotate
    def __setitem__(self, item: str, value):
        self.namespace[item] = value

    def __init__(self, store=None, **params):
        from . import builtin

        self.namespace = Namespace()
        self.namespace.vars.update(params)
        self.namespace.vars['store'] = store
        for attr_name in dir(self):
            if not attr_name.startswith("_"):
                try:
                    self.namespace[attr_name] = getattr(self, attr_name)
                except:
                    pass
        self.init()
        if not self._component_:
            self._instructions_ = execute(
                self._code_ or self.__doc__ or r"\frame"
            )
            self._component_ = self._instructions_.eval(
                self.namespace, ModularNamespace(builtin)
            )

    def render(self, master):
        self._component_.create(master)
        self.container = self._component_.container

    def update(self):
        self.namespace._watch_changes_()
        self._component_.update()

    def expose(self, func):
        self.namespace[func.__name__] = func


def component(func):
    def component_init(self):
        var = func(self)
        if var is not None:
            self.namespace.vars.update(var)
    return type(
        func.__name__,
        (Component,),
        {
            "init": component_init,
            "__doc__": func.__doc__,
        }
    )


from .instructions import Namespace
