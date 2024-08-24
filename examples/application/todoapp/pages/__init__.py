r"""
\frame padding=30
    \frame pos:grid=0,0  padding=5 pos:sticky=''
        \label text=[pages.index.welcome] pos:grid=0,0 font="{courier 10 bold}"
    \button pos:grid=0,1 text=[pages.index.next] pos:sticky='nse' command={gt_next}
"""

from taktk.component import Component

from . import todos
from taktk.notification import Notification


class Index(Component):
    code = __doc__

    def gt_next(self):
        import taktk

        taktk.application("todos")


def handle():
    return Index()
