from taktk.component import Component
from taktk.notification import Notification

from taktk.page import register_urlpattern


from ..admin import User

from . import todos


class Index(Component):
    r"""
    \frame padding=0
        \frame pos:pack pos:fill=BOTH
            \sdown.view text=@pages.index.welcome width=110 scrollable=False\
                pos:pack pos:fil=BOTH
        !if User.is_login()
            \ctk.button pos:pack text=@pages.index.next  command={gt_next}
        !if not User.is_login()
            \ctk.button pos:pack text=@pages.index.login command={gt_login}
    """
    items = range(5)

    def gt_next(self):
        import taktk

        taktk.application("todos")

    def gt_login(self):
        import taktk

        taktk.application("sign", "signin", redirect="todos")

    User = User


def default(store, /, **params):
    return Index()


@register_urlpattern("<uuid>")
def user(uuid: str):
    return User.from_uuid(uuid)
