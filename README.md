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
  \\frame pos:grid=0,0  padding=5
    \\label text={label_text} pos:grid=0,0
    \\button text='close >' command={close} pos:grid=1,0
  \\frame pos:grid=0,1  padding=5 relief='sunken'
    \\label text={{number}} pos:grid=0,0
    \\ctk.button text='add +' command={add} pos:grid=1,0"""
    code = __doc__

    label_text = 'close the window'
    number = 0

    def close(self):
        root.destroy()
        print("closed")

    def add(self):
        self['number'] += 1
        self.update()


root = Tk()

component = Comp()
component.render(root).grid(column=0, row=0)

root.mainloop()
```

![demo](images/example-simple.png)

> [!WARNING]
> The component building language is still in development and may be extremely
> strict


## Example 2: A todo list

```python
r"""
\frame
    \ctk.frame pos:grid=0,0 width=350 pos:sticky='nsew'
        \ctk.entry width=300 pos:grid=0,0 text={{entry}} pos:xweight=2
        \button text='+' command={add_todo} pos:grid=1,0 pos:xweight=0
    \ctk.frame pos:grid=0,1 width=350 pos:sticky='nsew'
        !enum todos:(i, todo)
            \ctk.label text={str(i + 1) + ') ' + todo } pos:grid={(0, i)} pos:sticky='nsw' bind:1={popper(i)}
            # popper closure does popping for you
"""
from tkinter import Tk
from taktk.component import Component


class Todo(Component):
    code = __doc__

    todos = []
    entry = "Enter todo here"

    def close(self):
        root.destroy()

    def add_todo(self):
        self.todos.append(self['entry'])
        self.entry = ""
        self.update()

    def clear(self):
        self.todos.clear()
        self.update()

    def popper(self, idx):
        def func(e):
            self.todos.pop(idx)
            self.update()
        return func


root = Tk()
root.title('Todo list')

editor = Todo()
editor.render(root).grid(column=0, row=0)

root.mainloop()
```

![demo](images/example-todo.png)
