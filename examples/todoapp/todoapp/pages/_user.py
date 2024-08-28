from taktk.component import Component
import taktk


class User(Component):
    r"""
    \frame weight:x='0: 10, 1: 2, 2: 10' padding=50
        \label text={user.name} pos:grid=0,0 pos:sticky='w' font='arial 20'
    """

    def __init__(self, user):
        self.user = user
        super().__init__()


def handle(store, user):
    return User(user=user)
