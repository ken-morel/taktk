from taktk.component import Component
from taktk.notification import Notification
from taktk.menu import Menu
from dataclasses import dataclass
from functools import cache


class Todo(Component):
    r"""
    \frame padding=20
        \frame pos:grid=0,0 pos:sticky='nsew'
            \entry width=80 pos:grid=0,0 text={{entry}} pos:sticky='nsw' bind:Key-Return={add_todo}
            \button text='+' command={add_todo} pos:grid=1,0 pos:sticky='nse'
        \frame pos:grid=0,1 pos:sticky='nsew'
            !enum todos:(idx, todo)
                \label bootstyle={'info' if todo.done else 'danger'} text={str(idx + 1) + ') ' + todo.desc} pos:grid={(0, idx)} pos:xweight=10 pos:sticky='nswe' bind:1={toggler(idx)} bind:3={popup_menu(idx)}
                \button text={_('pages.todos.mark-done') if not todo.done else _('pages.todos.mark-undone')} command={toggler(idx)} pos:grid={(1, idx)} pos:sticky='nse'
                \button text=[pages.todos.remove] command={popper(idx)} pos:grid={(2, idx)} pos:sticky='nse'
    """
    entry = ""
    todos = []

    def init(self):
        self.entry = _("pages.todos.placeholder")
        self.todos = []

    def close(self):
        root.destroy()

    def add_todo(self, *_):
        if not self.entry.strip():
            return Notification(
                "Empty field",
                "Please, enter an item",
                icon=r"C:\taktk\images\example-simple.png",
                duration=10000,
                bootstyle="warning",
                source="todo-empty-notification",
            ).show()
        self.todos.append(TodoItem(desc=self.entry))
        self.entry = ""
        self.update()

    def clear(self):
        self.todos.clear()
        self.update()

    def popper(self, idx):
        def func(*_):
            self.todos.pop(idx)
            self.update()

        return func

    def toggler(self, idx):
        def func(*_):
            self.todos[idx].done = not self.todos[idx].done
            self.update()

        return func

    def popup_menu(self, idx):
        menu = Menu(
            {
                "@toggle": self.toggler(idx),
                "@remove": self.popper(idx),
                "@edit": self.editer(idx),
            },
            translations="pages.todos.menu",
        )

        def func(e):
            menu.post(e.x_root, e.y_root)

        return func

    def editer(self, idx):
        def edit(*_):
            from customtkinter import CTkInputDialog

            value = CTkInputDialog(
                text="Enter the new value", title="Todos"
            ).get_input()
            self.todos[idx].desc = value
            self.update()

        return edit


@cache
def handle():
    return Todo()
