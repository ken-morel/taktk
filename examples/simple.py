from tkinter import Tk
from taktk.component import Component


class Comp(Component):
    """\
\\frame
  \\frame pos:grid=0,0
    \\label text={label_text} pos:grid=0,0
    \\button text='close >' command={close} pos:grid=1,0
  \\frame pos:grid=0,1
    \\label:label_component text=1 pos:grid=0,0
    \\ctk.button text='add +' command={add} pos:grid=1,0"""
    code = __doc__

    label_text = 'close the window'

    def close(self):
        root.destroy()
        print("closed")

    def add(self):
        label = self.label_component.widget
        label['text'] = int(label['text']) + 1
        label.update()


root = Tk()

component = Comp()
component.render(root).grid(column=0, row=0)

root.mainloop()
