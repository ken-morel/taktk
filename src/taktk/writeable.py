from tkinter import StringVar, IntVar
from typing import Callable, Any
from functools import cached_property
from contextlib import contextmanager
from . import Nil


class Writeable:
    """
    Creates a monitorred writable object, storing
    a specific state and subscribers
    """

    def __init__(self, val: Any = None):
        """
        Creates the object with the specified value
        """
        self._value_ = val
        self.subscribers = set()

    def set(self, value: Any, warn: bool = True):
        """
        Sets the value of the Writeable, and warns
        notifiers except warn=False
        """
        self._value_ = value
        if warn:
            self.warn_subscribers()
        return self._value_

    def get(self):
        """
        Returns the value of the variable
        """
        return self._value_

    def subscribe(self, func: Callable):
        """
        Registers a function to be called when value
        changes
        """
        self.subscribers.add(func)

    def unsubscribe(self, func: Callable | int):
        self.subscribers.remove(func)

    def warn_subscribers(self):
        for subscriber in self.subscribers:
            subscriber()

    @cached_property
    def intvar(self):
        return WritableIntVar(self)

    @cached_property
    def stringvar(self):
        return WritableStringVar(self)

    @cached_property
    def booleanvar(self):
        return WritableBoolVar(self)


class NamespaceWriteable(Writeable):
    """
    Creates a Writeable from namespace and variable
    """

    @staticmethod
    def parse_path(text):
        from .component.parser import State, VARNAME

        begin = State(text=text)
        state = begin.copy()
        path = []
        assert (
            len(set(text) - (VARNAME | set("[]."))) == 0
        ), f"wrong value path for NamespaceWriteable {text!r}"
        while state:
            if state[...][0] in VARNAME:
                path.append("")
                while state and state[...][0] in VARNAME:
                    path[-1] += state[...][0]
                    state += 1
                continue
            elif state[...][0] == "[":
                c = 0
                path.append("")
                while state:
                    if state[...][0] == "[":
                        c += 1
                    elif state[...][0] == "]":
                        if c <= 0:
                            path[-1] += state[...][0]
                            break
                        else:
                            c -= 1
                    path[-1] += state[...][0]
                    state += 1
                state += 1
                continue
            elif state[...][0] == ".":
                state += 1
            else:
                raise Exception("wrong value", state[...])
        return tuple(path)

    def __init__(self, namespace, name: str):
        """
        Creates the listener on the namespace with defined name
        """
        self.namespace = namespace
        self.subscribers = set()
        self._base = None
        *self.base_path, self.name = self.parse_path(name)
        namespace._subscribe_(self.update)
        self.last = Nil

    def get(self) -> Any:
        """
        Gets value from namespace
        """
        try:
            obj = self.base
            if self.name.startswith("["):
                string = "obj" + self.name
                try:
                    return eval(string, locals(), self.namespace)
                except Exception as e:
                    raise NameError(
                        "Error resolving NamespaceWriteable", e, repr(string)
                    ) from e
            else:
                return getattr(obj, self.name)
        except AttributeError as e:
            raise NameError(e).with_traceback(e.__traceback__) from None

    def set(self, val: Any) -> None:
        """
        Sets value to namespace
        """
        obj = self.base
        if self.name.startswith("["):
            exec(
                "obj" + self.name + " = val",
                globals(),
                vars(self.namespace) | locals(),
            )
        else:
            setattr(obj, self.name, val)
        self.warn_subscribers()
        self.namespace._watch_changes_()

    @property
    def base(self):
        if self._base is None:
            self.get_base()
        return self._base

    def get_base(self):
        obj = self.namespace
        path = self.base_path
        for sub in path:
            if sub.startswith("["):
                obj = eval("obj" + sub, globals(), locals())
            else:
                obj = getattr(obj, sub)
        self._base = obj

    def warn_subscribers(self):
        super().warn_subscribers()
        self.last = self.get()

    def update(self) -> bool:
        try:
            val = self.get()
        except NameError:
            pass
        else:
            if self.get() != self.last:
                self.warn_subscribers()
                return True
            else:
                return False


class WritableVar:
    _should_update_: bool = True
    _should_tk_update_: bool = True

    @contextmanager
    def no_writable_update(self):
        self._should_update_ = False
        yield
        self._should_update_ = True

    @contextmanager
    def no_tk_update(self):
        self._should_tk_update_ = False
        yield
        self._should_tk_update_ = True

    def __init__(self, writable):
        self._writable_ = writable
        writable.subscribe(self._update_)
        self.trace_add("write", self._tk_update_)

    def _tk_update_(self, varname, _, event):
        if self._should_tk_update_:
            with self.no_writable_update():
                self._writable_.set(self.get())
                self.set(self._writable_.get())


class WritableStringVar(StringVar, WritableVar):
    def __init__(self, writable):
        super().__init__(value=writable.get())
        WritableVar.__init__(self, writable)

    def _update_(self):
        if self._should_update_:
            with self.no_tk_update():
                self.set(self._writable_.get())


class WritableIntVar(IntVar, WritableVar):
    def __init__(self, writable):
        super().__init__(value=writable.get())
        WritableVar.__init__(self, writable)

    def _update_(self):
        if self._should_update_:
            with self.no_tk_update():
                self.set(self._writable_.get())


class WritableBoolVar(IntVar, WritableVar):
    def __init__(self, writable):
        super().__init__(value=writable.get())
        WritableVar.__init__(self, writable)

    def _update_(self):
        if self._should_update_:
            with self.no_tk_update():
                self.set(bool(self._writable_.get()))


class Expression(NamespaceWriteable):
    def __init__(self, namespace, expr: str):
        """
        Creates the listener on the namespace with defined name
        """
        self.namespace = namespace
        self.expr = expr
        self.subscribers = set()
        namespace._subscribe_(self.update)
        try:
            self.last = self.get()
        except:
            self.last = Nil

    def eval(self):
        return eval(self.expr, {}, self.namespace)

    def get(self) -> Any:
        """
        Gets value from namespace
        """
        return self.eval()

    def set(self, val: Any) -> None:
        """
        Sets value to namespace
        """
        pass

    def warn_subscribers(self):
        super().warn_subscribers()
        self.last = self.get()

    def update(self) -> bool:
        try:
            val = self.get()
        except Exception:
            pass
        else:
            if val != self.last:
                self.warn_subscribers()
                return True
            else:
                return False


def resolve(val):
    if isinstance(val, Writeable):
        return val.get()
    else:
        return val
