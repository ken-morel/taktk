# taktk
> **Order your tkinter apps.**
> 
**taktk** is a powerful, declarative, and component-driven framework that brings modern web-development paradigms to Python's Tkinter.
The name originates from *atak*, meaning "to order," with *tak* acting as the verb form. **taktk** literally translates to *ordering Tkinter*—taking the traditionally procedural, boilerplate-heavy process of building desktop GUIs and transforming it into a clean, reactive, and highly structured experience.
Built on top of ttkbootstrap (with support for customtkinter), taktk features its own Domain-Specific Language (DSL) embedded directly in Python docstrings, full state reactivity, web-style routing, an integrated HTTP server for deep linking, and native markdown rendering.
## ✨ Features & Advantages
### 🧩 Declarative Component Architecture
Forget writing endless widget.pack() and widget.grid() statements. **taktk** allows you to build modular Component classes where the UI layout is defined entirely via a custom docstring DSL.
 * Use structural tags like \frame, \button, and \label.
 * Inject dynamic Python expressions directly into widget attributes using {expression}.
 * Support for declarative logic like !if condition: and !enum iterable:(index, item) to map over data structures and conditionally render UI elements natively.
### ⚡ Deep Two-Way Reactivity
State management in Tkinter is notoriously clunky. **taktk** abstracts StringVar and IntVar behind a seamless reactivity engine.
 * Bind widget inputs directly to class attributes using {{attribute}}.
 * When the underlying data model updates, the UI updates automatically.
 * Attach event handlers cleanly using bind:1={method} or bind:Key-Return={method}.
### 🌐 Web-Style Routing & History
Build multi-page applications exactly like you would with a web framework.
 * **Page Views:** Navigate between different components using a robust URL-based routing system.
 * **Decorators:** Use @register_urlpattern to map Regex patterns, UUIDs, or strings directly to view functions (e.g., mapping /users/<uuid> to a specific user profile component).
 * **History:** Built-in back() and forward() navigation history.
### 🌍 First-Class Internationalization (i18n) & Theming
 * **Dynamic Dictionaries:** Define your application's text in YAML files (e.g., French.yml, English.yml).
 * **Reactive Translation:** Bind text in the UI using brackets text=[pages.index.welcome]. If the user changes the language at runtime, the entire UI updates instantly without a reload.
 * **Dynamic Theming:** Swap between ttkbootstrap themes (e.g., darkly, cosmo) on the fly.
### 🚀 Built-in HTTP Application Server
**taktk** ensures your application behaves like a modern app with its integrated threaded ApplicationServer.
 * **Singleton Locking:** Prevents multiple instances of your app from opening.
 * **Deep Linking:** If the app is already open, passing a route from the CLI (e.g., python main.py /todos) will ping the local server and instantly redirect the currently running instance to the new view.
### 📝 Native Markdown & Syntax Highlighting
Includes **Sdown**, a custom markdown parsing engine that renders natively into Tkinter Text widgets.
 * Supports headers, lists, and formatting.
 * Integrates pygments for full syntax highlighting of code blocks directly inside the desktop app.
### 💾 Built-in Store & ORM
Includes a JSON-backed persistence layer that acts like a lightweight ORM. Define Model classes (like User or Todo) that automatically serialize, generate UUIDs, and save to a local store.json.
## 🛠️ Quick Start
Here is how simple it is to build a fully reactive, persistent Todo application with inline styling, conditional rendering, and loop-based generation.
```python
from dataclasses import dataclass
from taktk.component import Component
from taktk.taktk import Application

@dataclass
class TodoItem:
    desc: str
    done: bool = False

class TodoApp(Component):
    r"""
    \frame padding=20
        \frame pos:grid=0,0 pos:sticky='nsew'
            # Two-way binding on the entry widget using {{entry}}
            \entry width=80 pos:grid=0,0 text={{entry}} pos:sticky='nsw' bind:Key-Return={add_todo}
            \button text='+' command={add_todo} pos:grid=1,0 pos:sticky='nse'
            
        \frame pos:grid=0,1 pos:sticky='nsew'
            # Iterate over the todos list and render components reactively
            !enum todos:(idx, todo)
                \label bootstyle={'info' if todo.done else 'danger'} \
                       text={str(idx + 1) + ') ' + todo.desc} \
                       pos:grid={(0, idx)} pos:sticky='nswe' \
                       bind:1={toggler(idx)}
                \button text={'Mark Undone' if todo.done else 'Mark Done'} \
                        command={toggler(idx)} pos:grid={(1, idx)}
                \button text='Remove' command={popper(idx)} pos:grid={(2, idx)}
    """

    todos = [TodoItem("Install taktk", True), TodoItem("Build an app", False)]
    entry = "Enter a new task..."

    def add_todo(self, *_):
        self.todos.append(TodoItem(desc=self["entry"]))
        self.entry = ""
        self.update()

    def toggler(self, idx):
        def func(*_):
            self.todos[idx].done = not self.todos[idx].done
            self.update()
        return func

    def popper(self, idx):
        def func(*_):
            self.todos.pop(idx)
            self.update()
        return func

if __name__ == "__main__":
    Application(layout=TodoApp()).run()

```
## 🏗️ Project Architecture
 * **taktk.component**: The core rendering engine that parses the docstring DSL and handles the component lifecycle (prerender, update, render).
 * **taktk.subscribe**: The reactivity tracking system for two-way variable bindings.
 * **taktk.page**: The PageView router handling Error404, redirects, and regex parameter extraction.
 * **taktk.dictionary**: The i18n module handling hot-swappable YAML language configurations.
 * **taktk.notification**: A non-blocking, stacking toast notification system.
 * **taktk.admin**: Base ORM logic providing Model generation for data storage.
## 📦 Requirements
 * Python 3.8+
 * ttkbootstrap
 * customtkinter (optional, experimental)
 * pyoload
 * PyYAML
 * Pillow
 * pygments (for Sdown syntax highlighting)
 * opencv-python (for experimental video/camera components)
## 📄 License
This project is licensed under the GPLv3.0 License.



---

## Side note

This was a project from 2024 when I was still from lower-sixth. The syntax of efus, including it's capabilitues improves a lot as I learned about existinf frameworks like svelte/reacr latter on see https://github.com/ken-morel/Efus.jl . Julia I considered more suited since it is dynamic and can generate Julia code from efus at macro expansion. But before this I even had to implement efus parser and interpreter in zig. Some times I get asked why I prefer sveltekit, and in fact it feels more natural and just feels right to do it that way.

