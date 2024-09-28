from ttkbootstrap import Window
from taktk.component import component


@component
def Simple(self):
    r"""
    \frame
        \label text={{text}} pos:pack
        \entry text={$text} pos:pack
    """
    text = "hello"
    return locals()


root = Window()
Simple().render(root).pack()

root.mainloop()
