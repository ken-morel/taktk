"""
Copyright (C) 2024  Ken Morel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import json
import os
import sys


class SettingsFile(dict):
    """
    Creates a json settings file at path
    """

    def __init__(self, path: str, default: dict = {}):
        """
        :param path: the path to the settings file
        """
        self.path = path
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
            return super().__setitem__(item, value)


_settings = None


def init(settings_path, default={}):
    global _settings
    if not _settings:
        _settings = SettingsFile(settings_path, default)


def reinit(settings_path):
    init(settings_path, force=True)


def get_setting(name, default=None):
    _settings.load()
    return _settings.get(name, default)


def set_setting(name, val):
    _settings[name] = val
    _settings.save()


def settings():
    return _settings
