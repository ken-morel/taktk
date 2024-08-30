import sys
from tkinter import BooleanVar
from tkinter import Image as TkImage
from tkinter import StringVar
from typing import Callable
from typing import Optional

from pyoload import annotate
from ttkbootstrap import Button
from ttkbootstrap import Checkbutton
from ttkbootstrap import Entry
from ttkbootstrap import Frame
from ttkbootstrap import Label

from ... import Nil
from ... import resolve
from ...media import Image
from ...writeable import NamespaceWriteable
from ...writeable import Writeable
from .. import _Component


class frame(_Component):
    WIDGET = Frame

    class attrs:
        bootstyle: str = Nil
        padding: int = Nil
        borderwidth: int = Nil
        relief: str = Nil
        width: int = Nil
        height: int = Nil

    same = [x for x in dir(attrs) if not x.startswith("_")]
    conf_aliasses = {
        **dict(zip(same, same)),
    }
    del same

    def create(self, parent: "Optional[_Component]" = None):
        super().create()
        parent = parent or self.parent.widget
        params = {
            **{
                self.conf_aliasses[k]: resolve(v)
                for k, v in vars(self.attrs).items()
                if k in self.conf_aliasses and v is not Nil
            }
        }
        self.widget = self.WIDGET(master=parent, **params)
        self.make_bindings()
        self._position_()
        for child in self.children:
            w = child.create(self.widget)
        return self.widget


class label(_Component):
    WIDGET = Label

    class attrs:
        bootstyle: str = Nil
        text: str = "fake"
        foreground: str = Nil
        background: str = Nil
        text_color: str = Nil
        padx: int = Nil
        pady: int = Nil
        font: str = Nil
        image: Image | TkImage = Nil
        compound: str = Nil

    same = [x for x in dir(attrs) if not x.startswith("_")]
    conf_aliasses = {
        **dict(zip(same, same)),
    }
    del same

    def create(self, parent: "Optional[_Component]" = None):
        super().create()
        parent = parent or self.parent.widget
        params = {
            **{
                self.conf_aliasses[k]: resolve(v)
                for k, v in vars(self.attrs).items()
                if k in self.conf_aliasses and v is not Nil
            }
        }
        self.widget = self.WIDGET(master=parent, **params)
        self._position_()
        self.make_bindings()
        return self.widget


class button(_Component):
    WIDGET = Button

    class attrs:
        bootstyle: str = Nil
        text: str = "fake"
        command: Callable = lambda: None
        padx: int = Nil
        pady: int = Nil
        fg: str = Nil
        bg: str = Nil
        image: Image | TkImage = Nil
        compound: str = Nil
        background: str = Nil
        foreground: str = Nil

    same = [x for x in dir(attrs) if not x.startswith("_")]
    conf_aliasses = {
        **dict(zip(same, same)),
    }
    del same

    def create(self, parent: "Optional[_Component]" = None):
        super().create()
        parent = parent or self.parent.widget
        params = {
            **{
                self.conf_aliasses[k]: resolve(v)
                for k, v in vars(self.attrs).items()
                if k in self.conf_aliasses and v is not Nil
            }
        }
        self.widget = self.WIDGET(master=parent, **params)
        self._position_()
        self.make_bindings()
        return self.widget


class entry(_Component):
    WIDGET = Entry

    class attrs:
        bootstyle: str = Nil
        text: str = "fake"
        padx: int = Nil
        pady: int = Nil
        width: int = Nil
        font: str = Nil
        textvariable: StringVar = Nil
        show: str = Nil

    same = [
        x for x in dir(attrs) if not x.startswith("_") and x not in ("text",)
    ]
    conf_aliasses = {
        **dict(zip(same, same)),
    }
    del same

    def create(self, parent: "Optional[_Component]" = None):
        super().create()
        parent = parent or self.parent.widget
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
        else:
            self.textvariable = params[textvariable]
        self.widget = self.WIDGET(
            master=parent,
            **params,
        )
        self._position_()
        self.make_bindings()
        return self.widget


class checkbutton(_Component):
    WIDGET = Checkbutton

    class attrs:
        bootstyle: str = Nil
        checked: bool = False
        padx: int = Nil
        pady: int = Nil
        width: int = Nil
        variable: BooleanVar = Nil

    same = [
        x
        for x in dir(attrs)
        if not x.startswith("_") and x not in ("checked",)
    ]
    conf_aliasses = {
        **dict(zip(same, same)),
    }
    del same

    def create(self, parent: "Optional[_Component]" = None):
        super().create()
        parent = parent or self.parent.widget
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
        self.widget = self.WIDGET(
            master=parent,
            **params,
        )
        self._position_()
        self.make_bindings()
        return self.widget
