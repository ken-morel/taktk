"""Base module containing taktk built-in components."""

from dataclasses import field
from tkinter import BooleanVar
from tkinter import Image as TkImage
from tkinter import StringVar
from tkinter.ttk import Button, Checkbutton, Entry, Frame, Label
from typing import Callable, Optional

from . import Nil, NilType, resolve
from . import media, writeable, component


class frame(component.TkComponent):
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


class label(component.TkComponent):
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
        image: media.Image | TkImage | NilType = Nil
        compound: str | NilType = Nil


class button(component.TkComponent):
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
        image: media.Image | TkImage | NilType = Nil
        compound: str | NilType = Nil
        background: str | NilType = Nil
        foreground: str | NilType = Nil


class entry(component.TkComponent):
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
        show: str | NilType = Nil
        bind: dict = field(default_factory=dict)

    def create(self, parent: "Optional[component.BaseComponent]" = None):
        super().create(parent)
        self.container["textvariable"] = self.attrs._get_writeable(
            "text"
        ).stringvar


class checkbutton(component.TkComponent):
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

    def create(self, parent: "Optional[component.BaseComponent]" = None):
        component.BaseComponent.create(self)
        parent = parent
        params = {
            **{
                self.conf_aliasses[k]: resolve(v)
                for k, v in vars(self.attrs).items()
                if k in self.conf_aliasses and v is not Nil
            }
        }
        if "variable" not in params:
            if isinstance(self.attrs.checked, writeable.Writeable):
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


class sdown:
    from .sdown import LexedCode as code
    from .sdown import SdownViewer as view


try:
    from customtkinter import CTkButton, CTkEntry, CTkFrame, CTkLabel
except ImportError:
    pass
else:

    class ctk:
        class frame(frame):
            Widget = CTkFrame

        class label(label):
            Widget = CTkLabel

            class attrs:
                text: str = "fake"
                fg_color: str = Nil
                bg_color: str = Nil
                text_color: str = Nil
                padx: int = Nil
                pady: int = Nil
                font: str = Nil

        class button(button):
            Widget = CTkButton

        class entry(entry):
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

            Widget = CTkEntry
