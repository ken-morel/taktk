import json
import os
from logging import getLogger

log = getLogger(__name__)


class Store(dict):
    """
    Creates a json settings file at path
    """

    def __init__(self, path: str, default: dict = {}):
        """
        :param path: the path to the settings file
        """
        self.path = path
        self.page_stores = {}
        super().__init__(default)
        try:
            self.load()
        except Exception:
            self.save()

    def load(self):
        with open(self.path) as f:
            self.update(json.loads(f.read()))

    def save(self):
        with open(self.path, "w") as f:
            f.write(json.dumps(self, indent=2))

    def __getitem__(self, item):
        try:
            self.load()
        except Exception as e:
            log.info("while loading Store", self)
            log.error(e)
            raise
        if isinstance(item, tuple):
            obj = self
            for x in item:
                obj = obj[x]
            return x
        else:
            return super().__getitem__(item)

    def __setitem__(self, item, value):
        if isinstance(item, tuple):
            *path, item = item
            obj = self
            for x in path:
                obj = obj[x]
            obj[item] = value
        else:
            super().__setitem__(item, value)
        try:
            self.save()
        except Exception as e:
            log.info("while saving Store", self)
            log.error(e)
            raise

    def for_page(self, page, default={}):
        if page not in self.page_stores:
            self.page_stores[page] = Pagestore(self, page, default=default)
        return self.page_stores[page]

    def __hash__(self):
        return hash(self.path)


class Pagestore(Store):
    FORMAT = "__pageStore_{0}__"

    def __init__(self, store, page_name, default={}):
        self.store = store
        self.page = self.FORMAT.format(page_name)
        if self.page not in store or not isinstance(store[self.page], dict):
            store[self.page] = default

    def __setitem__(self, item, value):
        self.store[self.page][item] = value
        self.store.save()

    def __getitem__(self, item):
        return self.store[self.page][item]

    def save(self):
        self.store.save()
