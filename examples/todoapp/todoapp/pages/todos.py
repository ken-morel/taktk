import functools

import taktk.component
import taktk.menu
import taktk.page
import taktk.store

from ..admin import Todo as Todo
from ..admin import User


@taktk.component.component
def TodoPage(self):
    r"""
    \frame padding=20
        \frame pos:pack
            \entry width=80 pos:grid=0,0 text=$entry pos:pack\
                bind:Key-Return={add_todo}
            \button text='+' command={add_todo} pos:pack
        \frame pos:pack
            !enum todos:(idx, todo)
                \label bootstyle={'info' if todo.done else 'danger'}\
                    text={str(idx + 1) + ') ' + todo.desc} pos:grid={(0, idx)}\
                    pos:xweight=10 pos:sticky='nswe'\
                    bind:1={toggler(todo.uuid)} bind:3={popup_menu(todo.uuid)}
                \button\
                    text={_(f"pages.todos.mark-{'un' if todo.done else ''}done")}\
                    command={toggler(todo.uuid)} pos:grid={(1, idx)}\
                    pos:sticky='nse'
                \button text=@pages.todos.remove command={popper(todo.uuid)}\
                    pos:grid={(2, idx)} pos:sticky='nse'
    """

    class Attrs:
        user: User
        store: taktk.store.Store

    def close():
        root.destroy()

    def add_todo(*_):
        if not self["entry"].strip():
            return taktk.notify(
                "Empty field",
                "Please, enter an item",
                duration=1000,
                bootstyle="warning",
                source="todo-empty-notification",
            ).show()
        self.attrs.user.create_todo(self["entry"]).save()
        self["entry"] = ""
        self["todos"] = Todo.for_user(self.attrs.user)

    def popper(uuid):
        def func(*_):
            Todo.from_uuid(uuid).delete()
            self["todos"] = Todo.for_user(self.attrs.user)

        return func

    def toggler(uuid):
        def func(*_):
            obj = Todo.from_uuid(uuid)
            obj.done = not obj.done
            obj.save()
            self["todos"] = Todo.for_user(self.attrs.user)

        return func

    def popup_menu(uuid):
        menu = taktk.menu.Menu(
            {
                "@toggle": toggler(uuid),
                "@remove": popper(uuid),
                "@edit": editer(uuid),
            },
            translations="pages.todos.menu",
        )

        def func(e):
            menu.post(e.x_root, e.y_root)

        return func

    def editer(uuid):
        def edit(*_):
            from customtkinter import CTkInputDialog

            value = CTkInputDialog(
                text="Enter the new value", title="Todos"
            ).get_input()
            todo = Todo.from_uuid(uuid)
            todo.desc = value
            todo.save()
            self["todos"] = Todo.for_user(self.attrs.user)

        return edit

    def update_entry():
        self.attrs.store["entry"] = self["entry"]

    todos = Todo.for_user(self.attrs.user)
    entry = self.attrs.store["entry"]

    self.subscribe_to(self.namespace, update_entry)
    return locals()


@functools.cache
def default(store, /):
    if User.is_login():
        user = User.current()
        return TodoPage(
            user=user,
            store=store.for_page(__name__).partition(
                user.name,
                {
                    "entry": _("pages.todos.placeholder"),
                },
            ),
        )
    else:
        raise taktk.page.Redirect("sign@signin")
