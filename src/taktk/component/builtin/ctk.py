from customtkinter import CTkLabel, CTkFrame, CTkButton, CTkEntry
from . import frame, label, button, entry




class frame(frame):
    WIDGET = CTkFrame


class label(label):
    WIDGET = CTkLabel


class button(button):
    WIDGET = CTkButton


class entry(entry):
    WIDGET = CTkEntry
