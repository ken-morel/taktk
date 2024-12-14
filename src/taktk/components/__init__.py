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

from efus.types import ENil as Nil
from efus.types import ENilType as NilT
from efus.types import ESize

from .. import component


from ttkbootstrap import Label
from ttkbootstrap import Window


class Window(component.TkComponent):
    class ParamsClass:
        title: NilT | str = Nil
        themename: NilT | str = Nil
        iconphoto: NilT | str = Nil
        size: NilT | ESize = Nil
        pos: NilT | ESize = Nil
        minsize: NilT | ESize = Nil
        maxsize: NilT | ESize = Nil
        hdpi: NilT | bool = Nil
        overrideredirect: NilT | bool = Nil
        alpha: NilT | float = Nil

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

    WidgetClass = Window


class Label(component.TkComponent):
    class ParamsClass:
        bootstyle: NilT | str = Nil
        text: NilT | str = Nil
        pos: dict = {}

    widget_config = ("bootstyle", "text")
    widget_config_aliasses = {}

    WidgetClass = Label
