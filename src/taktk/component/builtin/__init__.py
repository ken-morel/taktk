from tkinter.ttk import Label, Frame, Button
from .. import _Component
from ... import Nil
from pyoload import annotate
from typing import Optional
from typing import Callable
import sys
from ...writeable import Writeable


class frame(_Component):
    WIDGET = Frame

    class attrs:
        padding: int = Nil
        borderwidth: int = Nil
        relief: str = Nil

    def create(self, parent: "Optional[_Component]" = None):
        parent = parent or self.parent.widget
        same = [x for x in dir(frame.attrs) if not x.startswith('_')]
        param_names = {
            **dict(zip(same, same)),
        }
        params = {
            **{
                param_names[k]: (v.get() if isinstance(v, Writeable) else v) for k, v in vars(self.attrs).items() if k in param_names and v is not Nil
            }
        }
        self.widget = self.WIDGET(master=parent, **params)
        self._position_()
        for child in self.children:
            child.create(self.widget)
        return self.widget


class label(_Component):
    WIDGET = Label

    class attrs:
        text: str = "fake"
        padding: int = 5
        fg_color: str = Nil
        bg_color: str = Nil
        text_color: str = Nil
        padx: int = Nil
        pady: int = Nil

    def create(self, parent: "Optional[_Component]" = None):
        parent = parent or self.parent.widget
        same = [
            'fg_color', 'bg_color', 'text_color' 'padx', 'pady', 'text'
        ]
        param_names = {
            **dict(zip(same, same)),
        }
        params = {
            **{
                param_names[k]: (v.get() if isinstance(v, Writeable) else v) for k, v in vars(self.attrs).items() if k in param_names and v is not Nil
            }
        }
        self.widget = self.WIDGET(
            master=parent, **params
        )
        self._position_()
        return self.widget


class button(_Component):
    WIDGET = Button

    class attrs:
        padding: int = 5
        text: str = "fake"
        command: Callable = lambda: None
        padx: int = Nil
        pady: int = Nil

    def create(self, parent: "Optional[_Component]" = None):
        parent = parent or self.parent.widget
        same = [
            'command', 'text', 'padx', 'pady',
        ]
        param_names = {
            **dict(zip(same, same)),
        }
        params = {
            **{
                param_names[k]: (v.get() if isinstance(v, Writeable) else v) for k, v in vars(self.attrs).items() if k in param_names and v is not Nil
            }
        }
        self.widget = self.WIDGET(
            master=parent,
            **params
        )
        self._position_()
        return self.widget

