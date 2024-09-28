"""
The main components tool.

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
from typing import Optional, Type, Any
from inspect import _empty

from pyoload import annotate

from . import Nil, resolve
from . import template, writeable

AttrSpec = dict[str, tuple[Type, Optional[Any]]]


class AttributeManager:
    """An object to manage component attributes."""

    _params: dict[AttrSpec]
    _subscriber: writeable.Subscriber
    _subscribeable: writeable.Subscribeable

    def __init__(self, component: "BaseComponent", kwargs: dict[str, str]):
        """Create the Attibute manager from component and args."""
        self._component = component
        self._params = {}
        for name, ann, default in component.get_params():
            self._params[name] = (ann, default)
        self._subscriber = writeable.Subscriber()
        self._subscribeable = writeable.Subscribeable()
        self._subscribe = self._subscribeable.subscribe
        self._args = {}
        self._last = None
        for key, value in kwargs.items():
            sub, val = template.evaluate_literal(
                value, self._component.namespace
            )
            self._args[key] = (sub, val)
            if sub:
                self._subscriber.subscribe_to(val, self._update)
        self._collect_values()

    def _update(self):
        vals = self._values.copy()
        self._collect_values()
        if self._values != vals:
            self._subscribeable.warn_subscribers()

    def _collect_values(self):
        self._values = {}

        def filters(val, get, ann, default):
            from . import media, writeable
            from tkinter import Image

            if val is Nil:
                val = default
            if ann is writeable.Writeable and isinstance(
                val, writeable.Writeable
            ):
                return val
            else:
                if get:
                    val = val.get()
                if ann is Image or (
                    isinstance(ann, type)
                    and issubclass(ann, Image)
                    and isinstance(val, media.Image)
                ):
                    val = val.get()
                if isinstance(val, media.Image):
                    print(val)
                return val

        def set_param(obj, key, value, annotation, default):
            get, val = value
            if ":" in key:
                pre, key = key.split(":", 1)

                if pre not in obj or not isinstance(obj[pre], dict):
                    obj[pre] = {}
                set_param(obj[pre], key, value, annotation, default)
            else:
                obj[key] = filters(val, get, annotation, default)

        for key, value in self._args.items():
            if key in self._params:
                ann, val = self._params[key]
            else:
                ann = val = None
            set_param(self._values, key, value, ann, val)

    def _get_writeable(self, name):
        val = self._args[name][1]
        if isinstance(val, writeable.Writeable):
            return val
        else:
            raise NotImplementedError("Sorry...")

    def __getattr__(self, attr: str):
        """Get attribute from values."""
        if attr[0] == "_":
            return super().__getattr__(attr)
        else:
            try:
                return self._values[attr]
            except KeyError as e:
                raise AttributeError() from e


class BaseComponent(writeable.Subscriber):
    """The base component class."""

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

    @classmethod
    def get_params(cls) -> tuple[tuple[str, type, Any]]:
        """Get an iterable of tuples (name, annotation, default)."""
        anns = {}
        params = []
        for name, ann in cls.Attrs.__annotations__.items():
            anns[name] = ann
        for name, val in vars(cls.Attrs).items():
            if name in anns:
                params.append((name, anns[name], val))
            else:
                params.append((name, _empty, val))
        return tuple(params)

    __init_subclass__ = _init_subclass

    def __init__(
        self,
        namespace: "writeable.Namespace" = {},
        parent=None,
        attrs: dict[str] = {},
        params: dict[str] = {},
    ):
        """Initialize Base Component."""
        writeable.Subscriber.__init__(self)
        self.children = []
        self.parent = parent
        self.namespace = namespace
        if parent is not None:
            self.parent.children.append(self)
        self.raw_attrs = attrs
        self.attrs = AttributeManager(self, attrs)
        self.attrs._subscribe(self, self._update)

    def bind_attrs(self, attrs: dict[str]):
        """Bind the specified attributes to the component."""
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
        self.attrs._collect_values()
        for child in self.children:
            child.update()
        self._update()

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
        if hasattr(self.attrs, "lay") and self.attrs.lay:
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


class TkComponent(BaseComponent):
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
                self.conf_aliasses[k]: v
                for k, v in self.attrs._values.items()
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
        for k, v in {
            self.conf_aliasses[k]: v
            for k, v in self.attrs._values.items()
            if k in self.conf_aliasses and v is not Nil
        }.items():
            if k == "text":
                self.container["text"] = v
            try:
                self.container.configure(**{k: v})
            except Exception:
                raise


class EnumComponent(BaseComponent):
    def __init__(
        self,
        object,
        namespace,
        alias: tuple[str, str],
        parent: "Optional[BaseComponent]" = None,
        instructions: list = [],
    ):
        self.children = []
        self.parent = parent
        self.parent_namespace = namespace
        self.object = object
        self.instructions = instructions  # instructions
        self.alias = alias
        if parent is not None:
            self.parent.children.append(self)

    def create(self, parent=None):
        parent = parent or self.parent.outlet
        self.render_parent = parent
        self.widgets = []
        for idx, val in enumerate(self.object.get()):
            aidx, aval = self.alias
            namespace = writeable.Namespace(parents=[self.parent_namespace])
            namespace[aidx] = idx
            namespace[aval] = val
            for instr in self.instructions:
                comp = instr._eval(namespace)
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


class IfComponent(BaseComponent):
    def __init__(
        self,
        condition,
        namespace,
        parent: "Optional[BaseComponent]" = None,
        instructions: list = [],
    ):
        self.children = []
        self.parent = parent
        self.namespace = namespace
        self.condition = condition
        self.instructions = instructions  # instructions
        if parent is not None:
            self.parent.children.append(self)

    def create(self, parent=None):
        parent = parent or self.parent.outlet
        self.render_parent = parent
        self.widgets = []
        self.condition.subscribe(self._update)
        if self.condition.get():
            for instr in self.instructions:
                comp = instr._eval(self.namespace)
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


class Component(BaseComponent):
    code: Optional[str] = None
    _template_cache: tuple[Optional[str], Optional[template.Template]] = (
        None,
        None,
    )

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

    def __init_subclass__(cls):
        cls.get_template()

    @classmethod
    def get_template(cls):
        code = cls.code or cls.__doc__
        if cls._template_cache[0] != code:
            cls._template_cache = code, template.Template.parse(code)
        return cls._template_cache[1]

    def __setitem__(self, item: str, value):
        self.namespace[item] = value

    def __init__(self, store=None, **params):
        writeable.Subscriber.__init__(self)
        self.namespace = writeable.Namespace()
        self.namespace.vars.update(params)
        self.namespace.vars["store"] = store
        self.subscribe_to(self.namespace, self.update)
        for attr_name in dir(self):
            if not attr_name.startswith("_"):
                try:
                    self.namespace[attr_name] = getattr(self, attr_name)
                except AttributeError:
                    pass
        self.init()
        self.renderred = False
        self._component_ = self.get_template().eval(self.namespace)

    def render(self, master):
        self._component_.create(master)
        self.rederred = True
        return self.container

    def update(self):
        if self.renderred:
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

    def create_tk(self, root=None):
        """Create the component in a full Tk window."""
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.render(root).grid(column=0, row=0, sticky="nsew")
        return root

    def popup(self, **params):
        """Create the component in a full Tk window."""
        from tkinter import Toplevel

        root = Toplevel()
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.render(root).grid(column=0, row=0, sticky="nsew")
        return root


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
