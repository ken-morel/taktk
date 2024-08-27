from taktk.component import Component

from . import todos
from taktk.notification import Notification


class Index(Component):
    r"""
    \frame padding=30 weight:x='1:5'
        \frame pos:grid=0,1  padding=5 pos:sticky=''
            \label text=[pages.index.welcome] pos:grid=0,0 font="{courier 10 bold}"
        \ctk.button pos:grid=0,2 text=[pages.index.next] pos:sticky='se' command={gt_next}
    """

    def gt_next(self):
        import taktk

        taktk.application("todos")


def handle():
    return Index()
