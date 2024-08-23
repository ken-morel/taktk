"""
_Component instructions

Copyright (C) 2024  ken-morel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from . import parser
from dataclasses import dataclass, field
from pyoload import *
from typing import Optional


class Instruction:
    pass


Attrs = dict[str]


# @annotate
class Create_Component(Instruction):
    """
    create_Component instruction to create a new widget
    :param name: The widget name
    :param params: The widget parameters
    """

    name: str
    attrs: Attrs
    alias: Optional[str]
    parent: "Optional[_Component]"
    children: list[Instruction]
    computed: bool = False

    def __init__(
        self,
        name: str,
        attrs: Attrs = {},
        alias: Optional[str] = None,
        parent: "Optional[_Component]" = None,
    ):
        self.name = name
        self.attrs = attrs
        self.alias = alias
        self.parent = parent

    @classmethod
    def next(cls, _state, parent: "Optional[_Component]" = None):
        """
        Gets the next Create_Component instruction
        """
        state, name, alias = parser.tag_name(_state)
        attrs = {}
        while len(state[state:]) > 0:
            nstate, key, val = parser.next_attr_value(state)
            state |= nstate
            attrs[key] = val

        _state |= state
        return cls(name=name, alias=alias, attrs=attrs, parent=parent)

    @annotate
    def eval(self, namespace: "Component", component_space):
        assert self.parent or self.name == "frame", (self.parent, self.name)
        parent = self.parent  # if self.parent is not None else None
        self.component = component_space[self.name](
            parent=parent, attrs=self.attrs, namespace=namespace
        )
        if self.alias is not None:
            namespace[self.alias] = self.component
        self.computed = True
        return self.component


def execute(text, namespace, component_space):
    line, *lines = text.splitlines()
    master = Create_Component.next(parser.State(line, 0)).eval(
        namespace, component_space
    )
    scope = [master]
    last_ind = 0
    for line in lines:
        ind = 0
        while line[ind * 2 :].startswith("  "):
            ind += 1
        if ind == last_ind:
            scope.pop()
        else:
            while last_ind >= ind:
                scope.pop()
                last_ind -= 1
        scope.append(
            c := Create_Component.next(
                parser.State(line, ind * 2), parent=scope[-1]
            ).eval(namespace, component_space)
        )
        last_ind = ind
    return master


from . import _Component, Component
