from taktk.component import Component

from . import todos
from taktk.notification import Notification
from ..admin import User


class Index(Component):
    r"""
    \frame padding=30 weight:x='1:5'
        \frame pos:grid=0,1  padding=5 pos:sticky=''
            \label text=[pages.index.welcome] pos:grid=0,0 font="{courier 10 bold}"
        !if User.is_login()
            \ctk.button pos:grid=0,2 text=[pages.index.next] pos:sticky='se' command={gt_next}
        !if not User.is_login()
            \ctk.button pos:grid=0,2 text=[pages.index.login] pos:sticky='se' command={gt_login}
    """

    def gt_next(self):
        import taktk

        taktk.application("todos")

    def gt_login(self):
        import taktk
        taktk.application("sign", "signin", redirect='todos')

    User = User


def handle():
    return Index()
