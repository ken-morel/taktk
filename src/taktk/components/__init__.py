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
from .. import menu
from efus.types import Binding
from efus.types import ENil as Nil
from efus.types import ENilType as NilT
from efus.types import ESize

from .. import component
from .. import subscribe


import ttkbootstrap
import typing


class Menu(component.TkComponent):
    class ParamsClass:
        structure: dict
        translation: str

    def prerender(self):
        self.menu = menu.Menu(
            self.args["structure"],
            None
            if self.args["translation"] is Nil
            else self.args["translation"],
        )
        self.menu.toplevel(self.parent.widget)
        return self.menu

    def update(self):
        self.menu.update()


class Window(component.TkComponent):
    class ParamsClass:
        title: str | NilT
        themename: str | NilT
        iconphoto: str | NilT
        size: ESize | NilT
        pos: ESize | NilT
        minsize: ESize | NilT
        maxsize: ESize | NilT
        hdpi: bool | NilT
        overrideredirect: bool | NilT
        alpha: float | NilT
        menu: dict | NilT

    widget_config = (
        "title",
        "themename",
        "iconphoto",
        "size",
        "alpha",
        "hdpi",
        "overrideredirect",
    )
    widget_config_aliasses = {"pos": "position"}

    WidgetClass = ttkbootstrap.Window


class Label(component.TkComponent):
    class ParamsClass:
        bootstyle: str | NilT
        text: str | NilT
        pos = component.PosSpec
        padx: int | NilT
        pady: int | NilT
        foreground: str | NilT
        background: str | NilT

    widget_config = (
        "bootstyle",
        "text",
        "foreground",
        "background",
        "padx",
        "pady",
    )
    widget_config_aliasses = {}

    WidgetClass = ttkbootstrap.Label


class Frame(component.TkComponent):
    class ParamsClass:
        bootstyle: str | NilT
        padding: int | NilT
        pos = component.PosSpec
        padding: int | NilT
        borderwidth: int | NilT
        relief: str | NilT
        width: int | NilT
        height: int | NilT
        font: str | NilT

    widget_config = (
        "bootstyle",
        "padding",
        "borderwidth",
        "relief",
        "width",
        "height",
        "font",
    )
    widget_config_aliasses = {}

    WidgetClass = ttkbootstrap.Frame


class Button(component.TkComponent):
    class ParamsClass:
        weight: dict = {}
        pos = component.PosSpec
        bootstyle: str | NilT
        text: str | NilT
        command: typing.Callable | NilT
        padx: int | NilT
        pady: int | NilT
        image: NilT
        compound: str | NilT
        background: str | NilT
        foreground: str | NilT

    widget_config = (
        "bootstyle",
        "text",
        "command",
        "padx",
        "pady",
        "fg",
        "bg",
        "image",
        "compound",
    )
    widget_config_aliasses = {}

    WidgetClass = ttkbootstrap.Button


class Entry(component.TkComponent):
    class ParamsClass:
        pos = component.PosSpec
        bootstyle: str | NilT
        width: int | NilT
        var: Binding | NilT

    def prerender(self):
        if self.args["var"] is not Nil:
            self.args["textvariable"] = subscribe.TkStringBinding(
                self.args["var"]
            )
        self.widget_config = self.widget_config + ("textvariable",)
        widget = super().prerender()
        # if self.args["var"] is not Nil:
        #     widget.setvar()
        return widget

    widget_config = ("bootstyle", "width")
    widget_config_aliasses = {}

    WidgetClass = ttkbootstrap.Entry


__all__ = [x for x in dir() if not x.startswith("_")]
