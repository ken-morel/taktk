from taktk.component import Component
from taktk.notification import Notification
from taktk.page import register_urlpattern

from ..admin import User
from . import todos


class Index(Component):
    r"""
    \frame padding=30 weight:x='1:5' weight:y='0:5'
        \frame pos:grid=0,1  padding=5 pos:sticky=''
            \label text=[pages.index.welcome] pos:grid=0,0 font='"Nova Round" 15'
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

        taktk.application("sign", "signin", redirect="todos")

    User = User


def handle(store, /, **params):
    return Index()


@register_urlpattern(
    r"[\da-f]{8}\-[\da-f]{4}\-[\da-f]{4}\-[\da-f]{4}\-[\da-f]{12}",
    position=0,
)
def user(uuid):
    return User.from_uuid(uuid)
