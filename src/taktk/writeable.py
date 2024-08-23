from typing import Callable, Any


class Writeable:
    """
    Creates a monitorred writable object, storing
    a specific state and subscribers
    """
    def __init__(self, val: Any=None):
        """
        Creates the object with the specified value
        """
        self._value_ = val
        self.subscribers = set()

    def set(self, value: Any, warn: bool=True):
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
        print(f"{func} subscrivbes to {self.name}")
        self.subscribers.add(func)

    def unsubscribe(self, func: Callable | int):
        self.subscribers.remove(func)

    def warn_subscribers(self):
        print("warning for change")
        for subscriber in self.subscribers:
            subscriber()


class NamespaceWriteable(Writeable):
    """
    Creates a Writeable from namespace and variable
    """

    def __init__(self, namespace, name: str):
        """
        Creates the listener on the namespace with defined name
        """
        self.namespace = namespace
        self.name = name
        self.last = self.get()
        self.subscribers = set()
        namespace._subscribe_(self.update)

    def get(self) -> Any:
        """
        Gets value from namespace
        """
        return self.namespace[self.name]

    def set(self, val: Any) -> None:
        """
        Sets value to namespace
        """
        self.warn_subscribers()
        self.namespace[self.name] = val

    def warn_subscribers(self):
        super().warn_subscribers()
        self.last = self.get()

    def update(self) -> bool:
        if self.get() != self.last:
            self.warn_subscribers()
            return True
        else:
            return False
