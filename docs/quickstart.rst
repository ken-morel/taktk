Quickstart
==================================================

To setup you taktk project there are two modes of uses:

- :ref:`as-a-library`
- :ref:`as-a-framework`


As a library
--------------------------------------------------

Taktk supports using it's different components separately.

.. code-block:: python

  from tkinter import Tk
  from taktk.component import component

  @component
  def Widget(self):
    r"""
    \frame
      \label text="Hello world" font={text_font} pos:pack
    """

    text_font = "Arial 20"
    return locals()

  root = Tk()
  Widget().render(root).pack()
  root.mainloop()
