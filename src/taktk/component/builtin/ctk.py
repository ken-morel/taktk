from customtkinter import CTkLabel, CTkFrame, CTkButton
from .. import _Component
from ... import Nil
from pyoload import annotate
from typing import Optional
from typing import Callable
import sys




class frame(_Component):
    WIDGET = CTkFrame

    class attrs:
        padding: int = 5

    def create(self, parent: "Optional[_Component]" = None):
        parent = parent or self.parent.widget
        same = [
        ]
        param_names = {
            **dict(zip(same, same)),
        }
        params = {
            **{
                param_names[k]: v for k, v in vars(self.attrs).items() if k in param_names and v is not Nil
            }
        }
        self.widget = self.WIDGET(master=parent)
        self._position_()
        for child in self.children:
            child.create(self.widget)
        return self.widget


class label(_Component):
    WIDGET = CTkLabel

    class attrs:
        text: str = "fake"
        padding: int = 5
        fg_color: str = Nil
        bg_color: str = Nil
        text_color: str = Nil

    def create(self, parent: "Optional[_Component]" = None):
        parent = parent or self.parent.widget
        same = [
            'fg_color', 'bg_color', 'text_color'
        ]
        param_names = {
            **dict(zip(same, same)),
        }
        params = {
            **{
                param_names[k]: v for k, v in vars(self.attrs).items() if k in param_names and v is not Nil
            }
        }
        self.widget = self.WIDGET(
            master=parent, text=self.attrs.text, **params
        )
        self._position_()
        return self.widget


class button(_Component):
    WIDGET = CTkButton

    class attrs:
        padding: int = 5
        text: str = "fake"
        command: Callable = lambda: None

    def create(self, parent: "Optional[_Component]" = None):
        parent = parent or self.parent.widget
        same = [
            'command', 'text'
        ]
        param_names = {
            **dict(zip(same, same)),
        }
        params = {
            **{
                param_names[k]: v for k, v in vars(self.attrs).items() if k in param_names and v is not Nil
            }
        }
        self.widget = self.WIDGET(
            master=parent,
            **params
        )
        self._position_()
        return self.widget
