import sys
from tkinter import BooleanVar
from tkinter import Image as TkImage
from tkinter import StringVar
from typing import Callable, Optional

from pyoload import annotate
from ttkbootstrap import Button, Checkbutton, Entry, Frame, Label

from ... import Nil, resolve
from ...media import Image
from ...sdown import LexedCode as code
from ...sdown import SdownViewer as view
from ...writeable import NamespaceWriteable, Writeable
from .. import _Component
