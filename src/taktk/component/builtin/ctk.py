from customtkinter import CTkLabel, CTkFrame, CTkButton, CTkEntry
from . import frame, label, button, entry
from ... import Nil


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
