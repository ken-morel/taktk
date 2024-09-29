import taktk
from taktk.component import component, Component
from taktk.notification import Notification

from ..admin import User


class Signin(Component):
    r"""
    \frame padding=100
        \frame pos:pack pos:fill=BOTH
            \frame pos:pack pos:fill=BOTH padding=20
                \label text=@pages.signin.label.name pos:pack=LEFT\
                    font='"Nova Square" 15'
                \entry text=$username\
                    pos:pack=RIGHT width=30 font='"Nova Square" 18'
            \frame pos:pack pos:fill=BOTH padding=20
                \label text=@pages.signin.label.password pos:pack=LEFT\
                    font='"Nova Square" 15'
                \entry show='*' text=$password\
                    pos:pack=RIGHT width=30 font='"Nova Square" 18'
        \frame pos:pack pos:fill=BOTH
            \button command={gt_signup} text=@pages.signin.gt_signup pos:pack=LEFT
            \button command={signin} text=@pages.signin.submit pos:pack=RIGHT
    """

    class Attrs:
        redirect: str = "/todos"

    username = ""
    password = ""

    def signin(self):
        name = self["username"]
        password = self["password"]
        try:
            user = User.login(name, password)
        except User.DoesNotExist:
            Notification(
                "Todos",
                "Wrong login: please verify credentials and re-enter",
                bootstyle="danger",
                source=None,
                duration=10000,
            ).show()
        else:
            Notification(
                "Todos",
                "Signin successful",
                bootstyle="info",
                source="signin-page",
                duration=5000,
            ).show()
            taktk.application.view.url(self.attrs.redirect)

    def gt_signup(self):
        taktk.application.view.url("sign#signup")


def signin(store, /, redirect="todos"):
    return Signin(redirect=redirect)


class Signup(Component):
    r"""
    \frame padding=100
        \frame pos:pack pos:fill=BOTH
            \frame pos:pack pos:fill=BOTH padding=20
                \label text=@pages.signin.label.name pos:pack=LEFT\
                    font='"Nova Square" 15'
                \entry text=$username\
                    pos:pack=RIGHT width=30 font='"Nova Square" 18'
            \frame pos:pack pos:fill=BOTH padding=20
                \label text=@pages.signin.label.password pos:pack=LEFT\
                    font='"Nova Square" 15'
                \entry show='*' text=$password2\
                    pos:pack=BOTTOM width=30 font='"Nova Square" 18'
                \entry show='*' text=$password\
                    pos:pack=RIGHT width=30 font='"Nova Square" 18'
        \frame pos:pack pos:fill=BOTH
            \button command={gt_signin} text=@pages.signin.gt_signin pos:pack=LEFT
            \button command={signup} text=@pages.signin.submit pos:pack=RIGHT
    """
    username = ""
    password = ""
    password2 = ""

    class Attrs:
        redirect: str = "/todos"

    def signup(self):
        name = self["username"]
        password = self["password"]
        if self["password"] != self["password2"]:
            Notification(
                "Todos",
                "Unmatching password",
                duration=5000,
                bootstyle="danger",
            ).show()
            return
        try:
            user = User.signup(name, password)
        except User.DoesExist:
            Notification(
                "Todos",
                "User already exists",
                bootstyle="danger",
                source=None,
                duration=10000,
            ).show()
        else:
            Notification(
                "Todos",
                "Signup successful",
                bootstyle="info",
                source="signin-page",
                duration=5000,
            ).show()
            taktk.application.view.url(self.attrs.redirect)

    def gt_signin(self):
        taktk.application.view.url("sign#signin")


def signup(store, /, redirect="todos"):
    return Signup(redirect=redirect)
