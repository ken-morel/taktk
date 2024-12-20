import contextlib

from efus import subscribe
from efus.types import Binding
from efus.types import EObject
from tkinter import BooleanVar
from tkinter import IntVar
from tkinter import StringVar


class TkVarBinding(Binding, subscribe.Subscribeable):
    """Binding tkinter variable binding with automatic updates."""

    __has_eobject_casters__ = True
    _should_update: bool = True
    _should_tk_update: bool = True
    subscriber: subscribe.Subscriber

    def cast_to(self, typ):
        if issubclass(typ, TkVarBinding):
            return typ(self)
        else:
            return typ(self.get())

    @classmethod
    def cast_from(cls, val):
        if isinstance(val, Binding):
            return cls(val)
        else:
            raise TypeError(f"Cannot cast from {type(val)} to {cls}")

    @contextlib.contextmanager
    def _no_binding_update(self):
        """Prevent updates from binding."""
        self._should_update = False
        yield
        self._should_update = True

    @contextlib.contextmanager
    def _no_tk_update(self):
        """Prevent updates from tkinter variable machinery."""
        self._should_tk_update = False
        yield
        self._should_tk_update = True

    def __init__(self, binding: Binding):
        """Create a tkinter variable binding to the Binding."""
        subscribe.Subscribeable.__init__(self)
        self.subscriber = subscribe.Subscriber()
        self._binding = binding
        self.subscriber.subscribe_to(binding, self._update)
        self.trace_add("write", self._tk_update)

    def _tk_update(self, varname, _, event):
        """Update object from tkinter machinery."""
        if self._should_tk_update:
            with self._no_binding_update():
                self._binding.set(self.get())
                self.set(self._binding.get())


class TkStringBinding(StringVar, TkVarBinding):
    """A tkinter StringVar binding to a binding."""

    def __init__(self, binding: Binding):
        """Create a TkStringBinding binded to `binding`."""
        StringVar.__init__(self, value=binding.get())
        TkVarBinding.__init__(self, binding)

    def _update(self):
        if self._should_update:
            with self._no_tk_update():
                self.set(self._binding.get())


class TkIntBinding(IntVar, TkVarBinding):
    """A tkinter IntVar binding to a binding."""

    def __init__(self, binding: Binding):
        """Create a TkIntBinding binded to `binding`."""
        IntVar.__init__(self, value=binding.get())
        TkVarBinding.__init__(self, binding)

    def _update(self):
        if self._should_update:
            with self._no_tk_update():
                self.set(self._binding.get())


class TkBoolBinding(IntVar, TkVarBinding):
    """A tkinter BooleanVar binding to a binding."""

    def __init__(self, binding: Binding):
        """Create a TkStringBinding binded to `binding`."""
        IntVar.__init__(value=binding.get())
        TkVarBinding.__init__(self, binding)

    def _update(self):
        if self._should_update:
            with self._no_tk_update():
                self.set(bool(self._binding.get()))
