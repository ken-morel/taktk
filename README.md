# taktk

taktk from from the [bulu](https://wikipedia.com/wiki/bulu) word
_tak_, meaning to order, and _tk_ for `tkinter`.

taktk aims to give you a more orderly, easy and responsive way to build tkinter
pages.
It is currently in build(since last 2 days), but I will expose on what it can
do now.

## hello world example

Here the example in [examples/simple.py](examples/simple.py)

```python
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
    \\button text='add +' command={add} pos:grid=1,0"""
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
```

![demo](images/example-simple.png)

> [!WARNING]
> The component building language is still in development and may be extremely
> strict

