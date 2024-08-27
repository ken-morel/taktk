from taktk.component import Component
from taktk.notification import Notification
import taktk
from ..admin import User


class Signin(Component):
    r"""
    \frame:form weight:x='0: 1' weight:y='0: 1' padding=20
        \frame:form pos:grid=0,0 weight:x='0:1'
            \frame pos:grid=0,0 padding=5
                \label text=[pages.signin.label.name] pos:grid=0,0 pos:sticky='w'
                \entry text={{username}} pos:grid=1,0 width=50 pos:sticky='e'
            \frame pos:grid=0,1 padding=5
                \label text=[pages.signin.label.password] pos:grid=0,0 pos:sticky='w'
                \entry text={{password}} pos:grid=1,0 width=50 pos:sticky='e'

        \ctk.button command={signin} text=[pages.signin.submit] pos:grid=0,1 pos:sticky='se'
    """

    def __init__(self, redirect):
        self.redirect = redirect
        super().__init__()

    username = ""
    password = ""

    def signin(self):
        name = self['username']
        password = self['password']
        try:
            user = User.login(name, password)
        except User.DoesNotExist:
            Notification(
                "Todos",
                "Wrong login: please verify credentials and re-enter",
                bootstyle='danger',
                source=None,
                duration=10000,
            ).show()
        else:
            Notification(
                "Todos",
                "Signin successful",
                bootstyle='info',
                source="signin-page",
                duration=5000,
            ).show()
            taktk.application.view.url(self.redirect)



def signin(redirect='todos'):
    return Signin(redirect=redirect)
