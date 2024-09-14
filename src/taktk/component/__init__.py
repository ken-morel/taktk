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

from dataclasses import dataclass, field
from importlib import import_module
from types import ModuleType
from typing import Optional

from pyoload import *
from pyoload import annotate

from .. import Nil, resolve
from ..writeable import Expression, Namespace, Writeable
from . import parser


class Instruction:
    def __str__(self):
        if len(self.children) == 0:
            return f"<{self.__class__.__name__}:{self._str_header()}>"
        else:
            text = f"<{self.__class__.__name__}:{self._str_header()}["
            for child in self.children:
                for line in str(child).splitlines():
                    text += "\n  " + line
            return text + "\n]"

    def _str_header(self):
        return "{}"


Attrs = dict[str]


# @annotate
class Create_Component(Instruction):
    """
    create_Component instruction to create a new widget
    :param name: The widget name
    :param params: The widget parameters
    """

    name: str
    attrs: Attrs
    alias: Optional[str]
    parent: "Optional[_Component]"
    children: list[Instruction]
    computed: bool = False

    def __init__(
        self,
        name: str,
        attrs: Attrs = {},
        alias: Optional[str] = None,
        parent: "Optional[_Component]" = None,
    ):
        self.name = name
        self.attrs = attrs
        self.alias = alias
        self.parent = parent
        if parent:
            self.parent.children.append(self)
        self.children = []

    def _str_header(self):
        return f"{self.name}, {repr(self.attrs)[:10]}...; &{self.alias}"

    @classmethod
    def next(cls, _state, parent: "Optional[_Component]" = None):
        """
        Gets the next Create_Component instruction
        """
        state, name, alias = parser.tag_name(_state)
        attrs = {}
        while len(state[state:]) > 0:
            nstate, key, val = parser.next_attr_value(state)
            state |= nstate
            attrs[key] = val

        _state |= state
        return cls(name=name, alias=alias, attrs=attrs, parent=parent)

    @annotate
    def _eval(self, namespace: Namespace):
        parent = self.parent
        assert (
            parent.computed
        ), "cannot compute children instructions before parent"
        self.component = get_component(self.name, namespace)(
            parent=parent.component, attrs=self.attrs, namespace=namespace
        )
        if self.alias is not None:
            namespace[self.alias] = self.component
        self.computed = True
        for child in self.children:
            child._eval(namespace)
        return self.component

    @annotate
    def eval(self, namespace: Namespace):
        self.component = get_component(self.name, namespace)(
            parent=None, attrs=self.attrs, namespace=namespace
        )
        if self.alias is not None:
            namespace[self.alias] = self.component
        self.computed = True
        for child in self.children:
            child._eval(namespace)
        return self.component


@annotate
class Create_Enum_Component(Instruction):
    """
    create_Component instruction to create a new widget
    :param name: The widget name
    :param params: The widget parameters
    """

    object_name: str
    alias: tuple[str, str]
    parent: "Optional[Instruction]"
    children: list[Instruction]
    computed: bool = False

    def __init__(
        self,
        name: str,
        alias: tuple[str, str] = None,
        parent: "Optional[Instruction]" = None,
    ):
        self.object_name = name
        self.alias = alias
        self.parent = parent
        self.children = []
        if parent:
            parent.children.append(self)

    @classmethod
    @annotate
    def next(cls, _state, parent: "Optional[Instruction]" = None):
        """
        Gets the next Create_Component instruction
        """
        state, name, alias = parser.next_enum(_state)
        _state |= state
        return cls(name=name, alias=alias, parent=parent)

    @annotate
    def _eval(self, namespace: Namespace):
        from ..writeable import NamespaceWriteable

        parent = self.parent
        self.component = EnumComponent(
            parent=parent.component,
            namespace=namespace,
            object=NamespaceWriteable(namespace, self.object_name),
            instructions=self.children,
            alias=self.alias,
        )
        self.computed = True
        return self.component

    def eval(*__, **_):
        raise NotImplementedError()


class Create_If_Component(Instruction):
    """
    create_Component instruction to create a new widget
    :param name: The widget name
    :param params: The widget parameters
    """

    condition: str
    alias: tuple[str, str]
    parent: "Optional[Instruction]"
    children: list[Instruction]
    computed: bool = False

    def __init__(
        self,
        condition: str,
        parent: "Optional[Instruction]" = None,
    ):
        self.condition = condition
        self.parent = parent
        self.children = []
        if parent:
            parent.children.append(self)

    @classmethod
    def next(cls, _state, parent: "Optional[Instruction]" = None):
        """
        Gets the next Create_If_Component instruction
        """
        state, condition = parser.next_if(_state)
        _state |= state
        return cls(condition=condition, parent=parent)

    def _eval(self, namespace: Namespace):
        from ..writeable import NamespaceWriteable

        parent = self.parent
        self.component = IfComponent(
            parent=parent.component,
            namespace=namespace,
            condition=Expression(namespace, self.condition),
            instructions=self.children,
        )
        self.computed = True
        return self.component

    def eval(*__, **_):
        raise NotImplementedError()


def parse_subinstructions(parent, lines, begin, indent, offset):
    base_ind = -1
    last_component = None
    target_idx = 0
    line_idx = 0
    for line_idx, line in enumerate(lines):
        if line_idx < max(target_idx, begin):
            continue
        if not line.strip():
            continue
        if indent == -1:
            indent = len(line) - len(line.lstrip())
        if base_ind == -1:
            base_ind = (len(line) - len(line.lstrip())) // indent
        if line.strip().startswith("#"):
            continue
        ind = len(line) - len(line.lstrip())
        if ind % indent != 0:
            raise ValueError("Unexpected indent", line)
        ind = ind // indent
        if ind < base_ind:
            return (line_idx - 1, parent)
        elif ind > base_ind:
            target_idx, _w = parse_subinstructions(
                last_component, lines, line_idx, indent, offset
            )
            target_idx += 1
            continue
        else:
            instr = line.strip()
            if instr[0] == "\\":
                last_component = Create_Component.next(
                    parser.State(line, ind * 2), parent=parent
                )
            elif instr[0] == "!":
                if instr.startswith("!enum"):
                    last_component = Create_Enum_Component.next(
                        parser.State(line, ind * 2), parent=parent
                    )
                elif instr.startswith("!if"):
                    last_component = Create_If_Component.next(
                        parser.State(line, ind * 2), parent=parent
                    )
                else:
                    raise ValueError("unknown special tag:", instr)
            else:
                raise ValueError("unknown tag:", instr)
        last_ind = ind
    return (line_idx, parent)


def execute(text):
    lines = list(filter(lambda l: bool(l.strip()), text.splitlines()))
    offset = min(len(l) - len(l.lstrip(" ")) for l in lines)
    lines = [l[offset:] for l in lines]
    line, *lines = lines
    indent = -1
    while not line.startswith("\\"):
        if not line.strip() or line[0] == "#":
            line, *lines = lines
            continue
        elif line[0].isspace():
            raise ValueError("Unallowed space in line:", line)
        elif c == "@":
            if line.startswith("@indent"):
                indent = int(line.split(" ")[1])
                line, lines = lines
            else:
                raise ValueError("Unrecognised meta parameter:", line)
        else:
            raise ValueError("Error parsing line", line)
    master = Create_Component.next(parser.State(line, 0))
    _, instr = parse_subinstructions(
        master,
        lines,
        0,
        indent=indent,
        offset=offset,
    )
    return instr


###############################################################################


def get_component(name, namespace=None):
    from . import builtin

    if name[0].islower():
        if "." in name:
            mod_path, name = name.rsplit(".", 1)
            mod = import_module(__package__ + ".builtin." + mod_path)
        else:
            mod = builtin
        if hasattr(mod, name):
            _component = getattr(mod, name)
            return _component
        else:
            raise NameError(f"{name} not in module {mod}")
    elif namespace is not None:
        return namespace[name]
    else:
        raise ValueError(f"component not found {name}")


class _Component:
    """
    The base component class
    """

    parent = None
    children: list
    _pos_ = None
    container = None
    outlet = None
    _aligner = None

    def _init_subclass(cls):
        if not hasattr(cls, "Attrs"):
            cls.Attrs = type(cls.__name__ + ".Attrs", (), {})
        cls.Attrs = dataclass(cls.Attrs)

    __init_subclass__ = _init_subclass

    def __init__(
        self,
        namespace: "Namespace" = {},
        parent=None,
        attrs: dict[str] = {},
        params: dict[str] = {},
    ):
        self.children = []
        self.parent = parent
        self.namespace = namespace
        if parent is not None:
            self.parent.children.append(self)
        self.raw_attrs = attrs
        self.bind_attrs(self.collect_params(attrs) | params)

    def bind_attrs(self, attrs: dict[str]):
        try:
            self.attrs = self.__class__.Attrs(**attrs)
        except TypeError as e:
            raise TypeError(
                f"error while binding arguments to {self.__class__!r}",
                e,
                self.Attrs,
            ) from None

    def _align_widget(self, widget, params: dict[str]):
        if self._children_align == "r":
            widget.grid(column=self._align_offset, row=0, **params)
        elif self._children_align == "c":
            widget.grid(row=self._align_offset, column=0, **params)
        else:
            raise ValueError("unknown align offset:", self._children_align)
        self._align_offset += 1

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

    def init_geometry(self):
        grid_params = ("sticky",)
        pack_params = (
            "side",
            "anchor",
            "expand",
            "fill",
            "ipadx",
            "padx",
            "ipady",
            "pady",
        )
        if hasattr(self.attrs, "lay"):
            lay = self.attrs.lay
            if "w" in lay:
                if "x" in lay["w"]:
                    layx = resolve(lay["w"]["x"])
                    if isinstance(layx, str):
                        layx = dict(
                            [
                                tuple(map(str.strip, x.split(":", 1)))
                                for x in layx.split(",")
                            ]
                        )
                    for col, weight in layx.items():
                        self.outlet.columnconfigure(
                            int(col), weight=int(weight)
                        )
                if "y" in lay["w"]:
                    layy = resolve(self.attrs.lay["w"]["y"])
                    if isinstance(layy, str):
                        layy = dict(
                            [
                                tuple(map(str.strip, x.split(":", 1)))
                                for x in layy.split(",")
                            ]
                        )
                    for col, weight in layy.items():
                        self.outlet.columnconfigure(
                            int(col), weight=int(weight)
                        )

        if hasattr(self.attrs, "pos"):
            pos = self.attrs.pos
            if "pack" in pos and pos["pack"]:
                params = {k: v for k, v in pos.items() if k in pack_params}
                if isinstance(pos["pack"], str):
                    params["side"] = pos["pack"]
                self.container.pack(**params)
            elif "grid" in pos:
                grid = {k: v for k, v in pos.items() if k in grid_params}
                coord = resolve(pos["grid"])
                if isinstance(coord, tuple):
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
                self.container.grid(**grid)

    def collect_params(self, raw_attrs: dict[str]):
        def set_param(obj, key, value):
            if ":" in key:
                pre, key = key.split(":", 1)

                if not pre in obj or not isinstance(obj[pre], dict):
                    obj[pre] = {}
                set_param(obj[pre], key, value)
            else:
                obj[key] = parser.evaluate_literal(value, self.namespace)

        attrs = {}
        for key, value in raw_attrs.items():
            set_param(attrs, key, value)
        return attrs


class TkComponent(_Component):
    Widget = None
    _attr_ignore = ()
    _params = None

    def __init_subclass__(cls):
        cls.Attrs = dataclass(cls.Attrs)
        same = [
            x
            for x in dir(cls.Attrs)
            if not x.startswith("_") and x not in cls._attr_ignore
        ]
        cls.conf_aliasses = {
            **dict(zip(same, same)),
        }
        del same

    def create(self, parent):
        super().create()
        self._params = params = {
            **{
                self.conf_aliasses[k]: resolve(v)
                for k, v in vars(self.attrs).items()
                if k in self.conf_aliasses and v is not Nil
            }
        }
        self._create(parent, params)
        self.make_bindings()
        self.init_geometry()
        for child in self.children:
            child.create(self.outlet)

    def _create(self, parent, params={}):
        self.outlet = self.container = self.Widget(parent, **params)

    def _update(self):
        params = {
            **{
                self.conf_aliasses[k]: resolve(v, self.update)
                for k, v in vars(self.attrs).items()
                if k in self.conf_aliasses and v is not Nil
            }
        }
        for k, v in params.items():
            try:
                self.container.configure(k, v)
            except:
                pass

    def update(self):
        params = {
            **{
                self.conf_aliasses[k]: resolve(v, self.update)
                for k, v in vars(self.attrs).items()
                if k in self.conf_aliasses and v is not Nil
            }
        }
        if params != self._params:
            self._update()
            self._params = params
        super().update()


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
        self.namespace = Namespace()
        self.namespace.vars.update(params)
        self.namespace.vars["store"] = store
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
            self._component_ = self._instructions_.eval(self.namespace)

    def render(self, master):
        self._component_.create(master)

    def update(self):
        self.namespace._watch_changes_()
        self._component_.update()

    def expose(self, func):
        self.namespace[func.__name__] = func

    @property
    def container(self):
        return self._component_.container

    @property
    def outlet(self):
        try:
            out = self["outlet"]
            if out is not None:
                return out.outlet
            else:
                return None
        except NameError:
            return None


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
        },
    )
