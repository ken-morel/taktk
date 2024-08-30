from customtkinter import CTkButton
from customtkinter import CTkEntry
from customtkinter import CTkFrame
from customtkinter import CTkLabel

from ... import Nil
from . import button
from . import entry
from . import frame
from . import label


class frame(frame):
    WIDGET = CTkFrame


class label(label):
    WIDGET = CTkLabel

    class attrs:
        text: str = "fake"
        fg_color: str = Nil
        bg_color: str = Nil
        text_color: str = Nil
        padx: int = Nil
        pady: int = Nil
        font: str = Nil


class button(button):
    WIDGET = CTkButton


class entry(entry):
    WIDGET = CTkEntry
