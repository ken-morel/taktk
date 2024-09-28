from ttkbootstrap import Window
from taktk.component import component


@component
def Simple(self):
    r"""
    \frame
        \label text=$text pos:pack
        \entry text=$text width=$width pos:pack
        \button command={click} pos:pack
    """

    def click():
        self["text"] += "+"
        self["width"] += 1

    width = 20
    text = "hello"
    return locals()


root = Window(themename="darkly")
Simple().render(root).pack()


root.mainloop()
