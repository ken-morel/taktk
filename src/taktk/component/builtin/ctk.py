from customtkinter import CTkLabel, CTkFrame, CTkButton
from . import frame, label, button




class frame(frame):
    WIDGET = CTkFrame


class label(label):
    WIDGET = CTkLabel


class button(button):
    WIDGET = CTkButton
