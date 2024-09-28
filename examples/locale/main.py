"""Very minimal taktk localization example."""
from tkinter import Tk

from taktk.component import component
from taktk.dictionary import Dictionary

french = Dictionary.from_file("dictionaries/french.yml", "french")
english = Dictionary.from_file("dictionaries/english.yml", "english")
english.install()


@component
def Comp(self):
    r"""
    \frame
        \frame pos:pack  padding=5
            \label text=@label.text pos:pack=LEFT
            \button text=@button.close command={close} pos:pack=RIGHT
        \frame pos:pack padding=5
            \label text=$number pos:pack=LEFT
            \button text=@button.add command={add} pos:pack=RIGHT
        \button pos:pack command={toggle} text=$btn_text
    """
    from builtins import _

    code = __doc__

    number = 0
    btn_text = _.language

    def close():
        root.destroy()
        print("closed")

    def add():
        self["number"] += 1

    def toggle():
        from builtins import _  # The object is expected to change

        if _.language == "english":
            french.install()
        else:
            english.install()
        self["btn_text"] = _.language

    return locals()


root = Tk()

component = Comp()
component.render(root).grid(column=0, row=0)

root.mainloop()
