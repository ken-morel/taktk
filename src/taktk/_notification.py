import time

from PIL import ImageTk, Image
from pyoload import *
from threading import Lock
from threading import Thread
from customtkinter import CTkFrame, CTkLabel, CTkToplevel, CTkFont
from .utility import scale_size

DEFAULT_ICON_WIN32 = "\ue154"
DEFAULT_ICON = "\u25f0"


class Notification:
    MARGIN = 10
    _STACK = []
    WIDTH = 350
    IMAGE_WIDTH = 100
    rearange_lock = Lock()

    def __init__(
        self,
        title,
        message,
        duration=None,
        alert=False,
        bg=None,
        icon=None,
        source=None,
    ):
        self.message = message
        self.title = title
        self.duration = duration
        self.source = source
        if isinstance(icon, str):
            image = Image.open(icon)
            w, h = image.size
            sc = Notification.IMAGE_WIDTH / w
            icon = ImageTk.PhotoImage(image.resize((int(w * sc), int(h * sc))))
        else:
            try:
                sc = Notification.IMAGE_WIDTH / icon.width()
                icon.config(
                    width=int(sc * icon.width()),
                    height=int(sc * icon.height()),
                )
            except Exception:
                pass
        self.icon = icon
        self.titlefont = None

    def show(self):
        self.root = window = CTkToplevel()
        window.overrideredirect(1)
        window.attributes("-alpha", 0.7)
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        window.attributes("-topmost", 1)

        root = CTkFrame(window)
        root.grid(column=0, row=0, sticky="nsew")

        if self.icon is not None:
            CTkLabel(
                root,
                image=self.icon,
                compound="image",
                anchor="nw",
            ).grid(row=0, column=0, rowspan=2, sticky=NSEW, padx=(5, 0))

        CTkLabel(
            root,
            text=self.title,
            font=CTkFont("arial", 20),
            anchor="nw",
        ).grid(row=0, column=1, sticky="nsew", padx=10, pady=(5, 0))

        CTkLabel(
            root,
            text=self.message,
            wraplength=scale_size(root, Notification.WIDTH - 130),
            anchor="nw",
        ).grid(row=1, column=1, sticky="nsew", padx=10, pady=(0, 5))

        window.bind("<ButtonPress>", self.hide)
        Notification.add(self)
        window.bell()

        if self.duration is not None:
            window.after(self.duration, self.hide)

    def hide(self, *_):
        """Destroy and close the toast window."""
        Notification.remove(self)

    def _hide(self):
        alpha = float(self.root.attributes("-alpha"))
        if alpha <= 0.1:
            self.root.destroy()
            Notification.position_widgets()
        else:
            self.root.attributes("-alpha", alpha - 0.1)
            self.root.after(25, self._hide)

    @classmethod
    def add(cls, notification):
        # for x in range(len(cls._STACK)):
        #     if cls._STACK[x].source == notification.source and notification.source is not None:
        #         cls._STACK[x] = notification
        #         return self.position_widgets()

        marg = Notification.MARGIN
        width = Notification.WIDTH
        notification.root.update_idletasks()

        height = notification.root.winfo_height()
        screen_height = notification.root.winfo_screenheight()

        while True:
            taken = 0
            for notif in Notification._STACK:
                taken += marg + notif.root.winfo_height()

            if screen_height - (taken + marg) < height:
                Notification.remove_earliset()
                continue
            else:
                break
        cls._STACK.append(notification)
        notification.root.geometry(f"{width}x{height}-{marg}-{taken+marg}")

    @classmethod
    def remove_earliset(cls):
        cls.remove(cls._STACK[0])

    @classmethod
    def remove(cls, notification):
        notification._hide()
        if notification in cls._STACK:
            cls._STACK.pop(cls._STACK.index(notification))

    @classmethod
    def position_widgets(cls):
        marg = cls.MARGIN

        for idx, notification in enumerate(cls._STACK):
            taken = 0
            height = notification.root.winfo_height()
            for notif in cls._STACK[:idx]:
                taken += marg + notif.root.winfo_height()

            pos2 = taken + marg
            swidth = notification.root.winfo_screenheight()
            while (swidth - notification.root.winfo_y() - height) > pos2:
                for notif in cls._STACK[idx:]:
                    notif.root.geometry(
                        f"-{marg}+{notif.root.winfo_y() + 1}",
                    )
                    notif.root.update_idletasks()
                # time.sleep(0.005)
            notification.root.geometry(f"-{marg}-{pos2}")
            notification.root.update_idletasks()
