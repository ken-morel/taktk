Welcome to taktk Documentation
==============================

taktk is a powerful, reactive Tkinter-based library for creating modern,
responsive GUI applications in Python. It offers a range of features to
simplify application development, enhance user experience, and streamline
internationalization.

Key Features
------------

1. Reactive Programming Model and Simplified Component Creation with `taktl`
-----------------------------

taktk is built on a reactive programming paradigm, allowing for dynamic and
efficient UI updates. This approach ensures that your application's interface
remains responsive and up-to-date with minimal effort.

taktk includes `taktl`, a layout system that simplifies the creation and management of UI components.

- Intuitive layout definitions
- Responsive design support
- Easy component nesting and organization
- Event-driven architecture
- Automatic UI updates based on data changes
- Efficient state management

.. code-block:: python

  from taktk import component

  @component
  def signin(self):
      r"""
      \frame  # The container
        \entry value={$name} pos:pack
        \label text={$name} pos:pack
      """
      name = "helo name"
      return locals()

2. Easy Internationalization with Dictionaries
----------------------------------------------
Seamlessly add multi-language support to your applications using taktk's
Dictionary class.

- Define translations using simple Python dictionaries
- Easy language switching at runtime
- Nested structures for organized translations
- Special keys for advanced customization

Example::

    from taktk.dictionary import Dictionary

    english = Dictionary({
        "file": {
            "__label__": "File",
            "new": "New",
            "open": "Open",
            "save": "Save",
        },
        "edit": {
            "__label__": "Edit",
            "copy": "Copy",
            "save": "Save",
        }
    })

    french = Dictionary({
        "file": {
            "__label__": "Fichier",
            "new": "Nouveau",
            "open": "Ouvrir",
            "save": "Enregistrer",
        },
        "edit": {
            "__label__": "Editer",
            "copy": "Copier",
            "save": "Enregistrer",
        }
    })

    # Switch language
    english.install()
    # or
    french.install()

    text = _("menu/file")

.. note:: Note

  The translations are better in an external :file:`.yaml` file than as a dictionary in
  code of course (●'◡'●).

3. Flexible and Dynamic Menus
-----------------------------
Create complex menu structures with ease using taktk's Menu class.

- Declarative menu definition using nested dictionaries
- Automatic label translation
- Support for both menubars and popup menus
- Easy runtime modifications

.. code-block:: python

  source
  from taktk.menu import Menu

  menu = Menu({
      "@file": {
          "@new": new_file_function,
          "@open": open_file_function,
          "@save": save_file_function
      },
      "@edit": {
          "@copy": copy_function,
          "@paste": paste_function
      }
  })

  # Bind as menubar
  menu.toplevel(root)
  # Or use as popup
  menu.popup((x, y))


4. Comprehensive Notification System
------------------------------------
Easily create and manage notifications in your application using taktk's built-in notification module.

- Customizable notification duration
- Support for icons

..

    from taktk import notify

    notify("Update Available",
           "A new version of the application is ready to install.",
           duration="5000",
           icon="path/to/update_icon.png")

.. code-block:: taktl

  !enum ama:(d, j)
  \frame yeah={colorama} padding=34
    \dkfkl k

Getting Started
---------------
- :doc:`installation`
- :doc:`quickstart`
- :doc:`whatsnew`
- :doc:`tutorials/index`


.. toctree::
  :maxdepth: 2
  :caption: Contents:

  installation
  quickstart
  tutorials/index
  whatsnew
