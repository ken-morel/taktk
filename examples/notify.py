from tkinter import Tk
from taktk.component import Component
from taktk.notification import Notification
from taktk.media import Image


class Notifica(Component):
    r"""
\frame
    \button image=!{ipy_image} command={notif_ipy}
"""

    code = __doc__

    label_text = "close the window"
    number = 0
    ipy_image = Image('../images.ipython.png', {})

    def notif_ipy(self):
        Notification(
            "Ipython",
            "Ipython notification",
            bootstyle="danger",
            image=self.ipy_image.tk,
        )


root = Tk()

notifica = Notifica()
notifica.render(root).grid(column=0, row=0)

root.mainloop()
