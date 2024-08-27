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

from dataclasses import dataclass, field
from pyoload import *
from typing import Optional
from ..writeable import Namespace


class Instruction:
    def __str__(self):
        if len(self.children) == 0:
            return f"<{self.__class__.__name__}:{self._str_header()}>"
        else:
            text = f"<{self.__class__.__name__}:{self._str_header()}["
            for child in self.children:
                for line in str(child).splitlines():
                    text += "\n  " + line
            return text + "\n]"

    def _str_header(self):
        return '{}'


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
        if parent:
            self.parent.children.append(self)
        self.children = []

    def _str_header(self):
        return f"{self.name}, {repr(self.attrs)[:10]}...; &{self.alias}"

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
    def _eval(self, namespace: Namespace, component_space):
        parent = self.parent
        assert parent.computed, "cannot compute children instructions before parent"
        self.component = component_space[self.name](
            parent=parent.component, attrs=self.attrs, namespace=namespace
        )
        if self.alias is not None:
            namespace[self.alias] = self.component
        self.computed = True
        for child in self.children:
            child._eval(namespace, component_space)
        return self.component

    @annotate
    def eval(self, namespace: Namespace, component_space):
        self.component = component_space[self.name](
            parent=None, attrs=self.attrs, namespace=namespace
        )
        if self.alias is not None:
            namespace[self.alias] = self.component
        self.computed = True
        for child in self.children:
            child._eval(namespace, component_space)
        return self.component


@annotate
class Create_Enum_Component(Instruction):
    """
    create_Component instruction to create a new widget
    :param name: The widget name
    :param params: The widget parameters
    """

    object_name: str
    alias: tuple[str, str]
    parent: "Optional[Instruction]"
    children: list[Instruction]
    computed: bool = False

    def __init__(
        self,
        name: str,
        alias: tuple[str, str] = None,
        parent: "Optional[Instruction]" = None,
    ):
        self.object_name = name
        self.alias = alias
        self.parent = parent
        self.children = []
        if parent:
            parent.children.append(self)

    @classmethod
    @annotate
    def next(cls, _state, parent: "Optional[Instruction]" = None):
        """
        Gets the next Create_Component instruction
        """
        state, name, alias = parser.next_enum(_state)
        _state |= state
        return cls(name=name, alias=alias, parent=parent)

    @annotate
    def _eval(self, namespace: Namespace, component_space):
        from ..writeable import NamespaceWriteable
        parent = self.parent
        self.component = EnumComponent(
            parent=parent.component,
            namespace=namespace,
            object=NamespaceWriteable(namespace, self.object_name),
            instructions=self.children,
            alias=self.alias,
            component_space=component_space,
        )
        self.computed = True
        return self.component

    def eval(*__, **_):
        raise NotImplementedError()



def parse_subinstructions(parent, lines, begin, indent, offset):
    base_ind = -1
    last_component = None
    target_idx = 0
    line_idx = 0
    for line_idx, line in enumerate(lines):
        if line_idx < max(target_idx, begin):
            continue
        if not line.strip():
            continue
        if indent == -1:
            indent = len(line) - len(line.lstrip())
        if base_ind == -1:
            base_ind = (len(line) - len(line.lstrip())) // indent
        if line.strip().startswith("#"):
            continue
        ind = len(line) - len(line.lstrip())
        if ind % indent != 0:
            raise ValueError("Unexpected indent", line)
        ind = ind // indent
        if ind < base_ind:
            return (line_idx - 1, parent)
        elif ind > base_ind:
            target_idx, _w = parse_subinstructions(last_component, lines, line_idx, indent, offset)
            target_idx += 1
            continue
        else:
            instr = line.strip()
            if instr[0] == "\\":
                last_component = Create_Component.next(
                    parser.State(line, ind * 2), parent=parent
                )
            elif instr[0] == "!":
                if instr.startswith("!enum"):
                    last_component = Create_Enum_Component.next(
                        parser.State(line, ind * 2), parent=parent
                    )
                else:
                    raise ValueError("unknown special tag:", instr)
            else:
                raise ValueError("unknown tag:", instr)
        last_ind = ind
    return (line_idx, parent)


def execute(text):
    lines = list(filter(lambda l: bool(l.strip()), text.splitlines()))
    offset = min(len(l) - len(l.lstrip(" ")) for l in lines)
    lines = [l[offset:] for l in lines]
    line, *lines = lines
    indent = -1
    while not line.startswith("\\"):
        if not line.strip() or line[0] == "#":
            line, *lines = lines
            continue
        elif line[0].isspace():
            raise ValueError("Unallowed space in line:", line)
        elif c == "@":
            if line.startswith("@indent"):
                indent = int(line.split(" ")[1])
                line, lines = lines
            else:
                raise ValueError("Unrecognised meta parameter:", line)
        else:
            raise ValueError("Error parsing line", line)
    master = Create_Component.next(parser.State(line, 0))
    _, instr = parse_subinstructions(
        master,
        lines,
        0,
        indent=indent,
        offset=offset,
    )
    return instr


from . import parser
from . import _Component, EnumComponent
