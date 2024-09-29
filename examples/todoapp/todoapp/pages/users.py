import taktk
from taktk.component import component

from ..admin import User


@component
def Users(self):
    r"""
    \frame padding=50 borderwidth=1 relief=SOLID
        \label text="Users" pos:pack
        !enum users:(_, user)
            \frame pos:pack pos:fill=X padding=20 borderwidth=1 relief=SOLID
                \label text={user.name} pos:pack=LEFT font='arial 20'
                \button bootstyle='info' text=@pages.users.view pos:pack=RIGHT\
                    command={{visit(user.uuid)}}
    """

    def visit(uuid):
        taktk.application(str(uuid))

    users = User.all()
    return locals()


def default(store):
    return Users()
