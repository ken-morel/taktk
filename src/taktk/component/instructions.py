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


class Instruction:
    pass


Attrs = dict[str]


class Namespace:
    def __init__(self, parents = []):
        self.parents = parents
        self.vars = {}

    def __getitem__(self, item):
        if item in self.vars:
            return self.vars[item]
        else:
            for parent in self.parents:
                try:
                    return parent[item]
                except:
                    continue
            else:
                raise NameError(item)


class ComponentNamespace(Namespace):
    def __init__(self, component, parents = []):
        self.parents = parents
        self.vars = component


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
        print("__eval on", self.__class__.__name__)
        parent = self.parent
        assert parent.computed, "cannot compute children instructions before parent"
        self.component = component_space[self.name](
            parent=parent.component, attrs=self.attrs, namespace=namespace
        )
        if self.alias is not None:
            setattr(namespace, self.alias, self.component)
        self.computed = True
        for child in self.children:
            child._eval(namespace, component_space)
        return self.component

    @annotate
    def eval(self, namespace: Namespace, component_space):
        print("eval on", self.__class__.__name__)
        self.component = component_space[self.name](
            parent=None, attrs=self.attrs, namespace=namespace
        )
        if self.alias is not None:
            namespace[self.alias] = self.component)
        self.computed = True
        for child in self.children:
            child._eval(namespace, component_space)
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
    def _eval(self, namespace: "_Component", component_space):
        print("eval on", self.__class__.__name__)
        self.component = component_space[self.name](
            parent=None, attrs=self.attrs, namespace=namespace
        )
        if self.alias is not None:
            setattr(namespace, self.alias, self.component)
        self.computed = True
        for child in self.children:
            child._eval(namespace, component_space)
        return self.component

    @annotate
    def _eval(self, namespace: Namespace, component_space):
        from ..writeable import NamespaceWriteable

        for
        parent = self.parent
        self.component = EnumComponent(
            parent=parent,
            namespace=namespace,
            object=NamespaceWriteable(namespace, self.object_name),
            alias=self.alias,
        )
        return self.component



def parse_subinstructions(parent, lines, begin, indent, offset):
    print("child")
    base_ind = -1
    last_component = None
    target_idx = 0
    for line_idx, line in enumerate(lines):
        if line_idx < target_idx or line_idx < begin:
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
        print(ind, base_ind, indent, line)
        if ind < base_ind:
            return (line_idx, parent)
        elif ind > base_ind:
            target_idx, _w = parse_subinstructions(last_component, lines, line_idx, indent, offset)
            print(target_idx, _w)
            continue
        else:
            instr = line.strip()
            if instr[0] == "\\":
                last_component = Create_Component.next(
                    parser.State(line, ind * 2), parent=parent
                )
            elif instr[0] == "!":
                if instr.startswith("!enum"):
                    Enum_Component.next(
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
    return parse_subinstructions(
        master,
        lines,
        0,
        indent=indent,
        offset=offset,
    )[1]


from . import parser
from . import _Component
