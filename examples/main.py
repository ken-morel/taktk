r"""\frame
  \frame pos:grid=0,0
    \label text='enter your name' pos:grid=0,0
    \button text='button n' command={close} pos:grid=0,1
  \frame pos:grid=0,1
    \frame pos:grid=0,0
"""

from customtkinter import CTk as Tk
from taktk.component import Component


class Comp(Component):
    code = __doc__

    def close(self):
        print("closed")


root = Tk()
# root.geometry("400x150")

comp = Comp()
comp.render(root).grid(column=0, row=0)

root.mainloop()
