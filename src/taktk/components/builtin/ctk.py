from dataclasses import field

from customtkinter import CTkButton, CTkEntry, CTkFrame, CTkLabel

from ... import Nil
from . import *


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
