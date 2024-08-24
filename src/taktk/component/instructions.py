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
        parent = self.parent  # if self.parent is not None else None
        self.component = component_space[self.name](
            parent=parent, attrs=self.attrs, namespace=namespace
        )
        if self.alias is not None:
            setattr(namespace, self.alias, self.component)
        self.computed = True
        return self.component


@annotate
class Enum_Component(Instruction):
    """
    create_Component instruction to create a new widget
    :param name: The widget name
    :param params: The widget parameters
    """

    object_name: str
    alias: tuple[str, str]
    parent: "Optional[_Component]"
    children: list[Instruction]
    computed: bool = False

    def __init__(
        self,
        name: str,
        alias: tuple[str, str] = None,
        parent: "Optional[_Component]" = None,
    ):
        self.object_name = name
        self.alias = alias
        self.parent = parent

    @classmethod
    def next(cls, _state, parent: "Optional[_Component]" = None):
        """
        Gets the next Create_Component instruction
        """
        state, name, alias = parser.next_enum(_state)
        _state |= state
        return cls(name=name, alias=alias, parent=parent)

    @annotate
    def eval(self, namespace: "Component", component_space):
        from ..writeable import NamespaceWriteable
        from . import EnumComponent

        parent = self.parent
        self.component = EnumComponent(
            parent=parent,
            namespace=namespace,
            object=NamespaceWriteable(namespace, self.object_name),
            alias=self.alias,
        )
        return self.component


def execute(text, namespace, component_space):
    line, *lines = text.splitlines()
    indent = -1
    while not line.startswith("\\"):
        if not line.strip() or line[0] == "#":
            line, *lines = lines
            continue
        elif c.isspace():
            raise ValueError("Unallowed space in line:", line)
        elif c == "@":
            if line.startswith("@indent"):
                indent = int(line.split(" ")[1])
                line, lines = lines
            else:
                raise ValueError("Unrecognised meta parameter:", line)
        else:
            raise ValueError("Error parsing line", line)
    master = Create_Component.next(parser.State(line, 0)).eval(
        namespace, component_space
    )
    scope = [master]
    last_ind = 0
    for line in lines:
        if not line.strip():
            continue
        if indent == -1:
            indent = len(line) - len(line.lstrip())
        if line.strip().startswith("#"):
            continue
        ind = len(line) - len(line.lstrip())
        if ind % indent != 0:
            raise ValueError("Unexpected indent", line)
        ind = ind // indent
        if ind == last_ind:
            scope.pop()
        else:
            while last_ind >= ind:
                scope.pop()
                last_ind -= 1
        instr = line.strip()
        if instr[0] == "\\":
            scope.append(
                Create_Component.next(
                    parser.State(line, ind * 2), parent=scope[-1]
                ).eval(namespace, component_space)
            )
        elif instr[0] == "!":
            if instr.startswith("!enum"):
                scope.append(
                    c := Enum_Component.next(
                        parser.State(line, ind * 2), parent=scope[-1]
                    ).eval(namespace, component_space)
                )
            else:
                raise ValueError("unknown special tag:", instr)
        else:
            raise ValueError("unknown tag:", instr)
        last_ind = ind
    return master


from . import _Component, Component
