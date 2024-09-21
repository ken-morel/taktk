from dataclasses import field
from tkinter import BooleanVar
from tkinter import Image as TkImage
from tkinter import StringVar
from tkinter.ttk import Button, Checkbutton, Entry, Frame, Label
from typing import Callable, Optional

from ... import Nil, NilType, resolve
from ...media import Image
from ...writeable import Writeable
from .. import TkComponent, _Component


class frame(TkComponent):
    Widget = Frame

    class Attrs:
        weight: dict = field(default_factory=dict)
        pos: dict = field(default_factory=dict)
        lay: dict = field(default_factory=dict)
        bind: dict = field(default_factory=dict)
        bootstyle: str | NilType = Nil
        padding: int | NilType = Nil
        borderwidth: int | NilType = Nil
        relief: str | NilType = Nil
        width: int | NilType = Nil
        height: int | NilType = Nil


class label(TkComponent):
    Widget = Label

    class Attrs:
        weight: dict = field(default_factory=dict)
        pos: dict = field(default_factory=dict)
        lay: dict = field(default_factory=dict)
        bind: dict = field(default_factory=dict)
        bootstyle: str | NilType = Nil
        text: str = "fake"
        foreground: str | NilType = Nil
        background: str | NilType = Nil
        text_color: str | NilType = Nil
        padx: int | NilType = Nil
        pady: int | NilType = Nil
        font: str | NilType = Nil
        image: Image | TkImage | NilType = Nil
        compound: str | NilType = Nil


class button(TkComponent):
    Widget = Button

    class Attrs:
        weight: dict = field(default_factory=dict)
        pos: dict = field(default_factory=dict)
        lay: dict = field(default_factory=dict)
        bind: dict = field(default_factory=dict)
        bootstyle: str | NilType = Nil
        text: str = "fake"
        command: Callable = lambda: None
        padx: int | NilType = Nil
        pady: int | NilType = Nil
        fg: str | NilType = Nil
        bg: str | NilType = Nil
        image: Image | TkImage | NilType = Nil
        compound: str | NilType = Nil
        background: str | NilType = Nil
        foreground: str | NilType = Nil


class entry(TkComponent):
    Widget = Entry
    _attr_ignore = ("text",)

    class Attrs:
        weight: dict = field(default_factory=dict)
        pos: dict = field(default_factory=dict)
        lay: dict = field(default_factory=dict)
        bootstyle: str | NilType = Nil
        text: str = "fake"
        padx: int | NilType = Nil
        pady: int | NilType = Nil
        width: int | NilType = Nil
        font: str | NilType = Nil
        textvariable: StringVar | NilType = Nil
        show: str | NilType = Nil
        bind: dict = field(default_factory=dict)

    def create(self, parent: "Optional[_Component]" = None):
        _Component.create(self)
        parent = parent
        params = {
            **{
                self.conf_aliasses[k]: resolve(v)
                for k, v in vars(self.attrs).items()
                if k in self.conf_aliasses and v is not Nil
            }
        }
        if "textvariable" not in params:
            if isinstance(self.attrs.text, Writeable):
                self.textvariable = self.attrs.text.stringvar
            else:
                self.textvariable = StringVar()
                self.textvariable.set(self.attrs.text)
            params["textvariable"] = self.textvariable
            self.attrs.textvariable = self.textvariable
        else:
            self.textvariable = params[textvariable]
        self.container = self.outlet = self.Widget(
            master=parent,
            **params,
        )
        self.init_geometry()
        self.make_bindings()


class checkbutton(TkComponent):
    Widget = Checkbutton
    _attr_ignore = ("checked",)

    class Attrs:
        weight: dict = field(default_factory=dict)
        pos: dict = field(default_factory=dict)
        lay: dict = field(default_factory=dict)
        bind: dict = field(default_factory=dict)
        bootstyle: str | NilType = Nil
        checked: bool = False
        padx: int | NilType = Nil
        pady: int | NilType = Nil
        width: int | NilType = Nil
        variable: BooleanVar | NilType = Nil
        _ignore = ("checked",)

    def create(self, parent: "Optional[_Component]" = None):
        _Component.create(self)
        parent = parent
        params = {
            **{
                self.conf_aliasses[k]: resolve(v)
                for k, v in vars(self.attrs).items()
                if k in self.conf_aliasses and v is not Nil
            }
        }
        if "variable" not in params:
            if isinstance(self.attrs.checked, Writeable):
                self.variable = self.attrs.checked.booleanvar
            else:
                self.variable = BooleanVar(value=self.attrs.checked)
            params["variable"] = self.variable
        else:
            self.variable = params["variable"]
        self.container = self.Widget(
            master=parent,
            **params,
        )
        self.outlet = None
        self.init_geometry()
        self.make_bindings()
