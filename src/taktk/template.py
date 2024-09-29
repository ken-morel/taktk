"""
Taktk templating engine.

Copyright (C) 2022  ken-morel

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
import dataclasses
import decimal
import enum
import os.path
import string
from decimal import Decimal
from pathlib import Path
from typing import Optional, Any

from pyoload import annotate

from . import dictionary, writeable, component


class TagType(enum.Enum):
    """Enum type for Template.Item `.type`."""

    TAG = enum.auto()
    SPECIAL = enum.auto()
    META = enum.auto()


SPACE = frozenset(" ")
VARNAME = frozenset(string.ascii_letters + string.digits + "_")
COMPONENT_NAME = VARNAME | frozenset(".")
BRACKETS = dict(map(tuple, "(),[],{}".split(",")))
STRING_QUOTES = frozenset("\"'")
INT = frozenset(string.digits)
DECIMAL = frozenset(string.digits + ".")
SLICE = INT | frozenset(":")
POINT = DECIMAL | frozenset(",")
ATTR_NAME = frozenset(":-") | VARNAME


class State:
    """Stores parser state and parsing utils."""

    __slots__ = ("text", "idx")
    text: str
    idx: int

    @annotate
    def __init__(self, text: str, idx: int = 0):
        """Initialize the parser state."""
        self.text = text
        self.idx = idx

    def __ior__(self, other: "State"):
        """Copy the other state object."""
        if not isinstance(other, State):
            return NotImplemented
        self.idx = other.idx
        return self

    def copy(self) -> "State":
        """Copy the state object."""
        return State(text=self.text, idx=self.idx)

    def __int__(self) -> int:
        """Convert state to int, return index."""
        return self.idx

    def __index__(self) -> int:
        """Use state as index, return index."""
        return self.idx

    def __iadd__(self, val) -> "State":
        """Add state index."""
        self.idx += val
        return self

    def __add__(self, val) -> int:
        """Add states."""
        return self.idx + val

    def __radd__(self, val) -> int:
        """Add states."""
        return self.idx + val

    def __gt__(self, val: int) -> bool:
        """Perform gt operation on state index."""
        return int.__gt__(self.idx, val)

    def __lt__(self, val: int) -> bool:
        """Perform lt operation on state index."""
        return int.__lt__(self.idx, val)

    def __hash__(self) -> int:
        """Compute a dummy hash based on text hash."""
        return self.idx * len(self.text) * hash(self.text)

    def __len__(self) -> int:
        """Compute the text length."""
        return len(self.text)

    def __getitem__(self, item: slice | int) -> str:
        """Slice the state text."""
        if item == ...:
            return self.text[self.idx]
        elif isinstance(item, slice):
            return self.text.__getitem__(
                slice(
                    *(
                        self.idx if x is ... else x
                        for x in (item.start, item.stop, item.step)
                    )
                )
            )
        else:
            return self.text.__getitem__(item)

    def __bool__(self) -> bool:
        """Return true if index did not exceed text length."""
        return self.idx < len(self.text)

    def next_line(self) -> bool:
        """Skip all characters till next newline character."""
        while self and self[...] != "\n":
            self += 1
        self += 1
        return bool(self)

    def skip_spaces(self) -> int:
        """Skip all spaces and return their number."""
        count = 0
        while self and self[...] in SPACE:
            self += 1
            count += 1
        if (
            self
            and self[self.idx] == "\\"
            and len(self) > self.idx + 1
            and self[self.idx + 1] == "\n"
        ):
            self += 2
            return count + self.skip_spaces()
        return count

    def next_tag_name(self) -> tuple[str, Optional[str]]:
        r"""Get next tag name from `\` character, may include alias."""
        self.skip_spaces()
        begin = self.copy()
        self += 1
        name = ""
        while self and self[...] in COMPONENT_NAME:
            self += 1
        name = self.text[begin + 1 : self]

        if len(self.text) > self and self.text[self] == ":":
            self += 1
            begin = self.copy()
            while (
                len(self.text) > int(self)
                and self.text[int(self)] in COMPONENT_NAME
            ):
                self += 1
            alias = self.text[begin : int(self)]
        else:
            alias = None
        return (name, alias)

    def next_attr_value(self) -> "tuple[State, str, str]":
        r"""Get next attribute value pair."""
        self.skip_spaces()
        attr = ""

        while self and self[...] in ATTR_NAME:
            attr += self[...]
            self += 1
        if not self or self[...] != "=":
            return attr, "True"
        else:
            self += 1
            val = self.next_value()
            return attr, val

    def next_value(self) -> str:
        """Read the next value in parser."""
        self.skip_spaces()
        begin = self.copy()
        brackets = []
        if (
            ":" in self[...:]
            and self[...:][: (n := self[...:].index(":"))].isalpha()
            and len(brackets) == 0
        ):
            begin = self.copy()
            self += n
            bc = 0
            while self:
                if self[...] == "{":
                    bc += 1
                elif self[...] == "}":
                    bc -= 1
                elif (quote := self[...]) in STRING_QUOTES:
                    self += 1
                    while self:
                        if self[...] == quote:
                            break
                        elif self[...] == "\\":
                            self += 2
                        else:
                            self += 1
                    else:
                        raise Exception(
                            "unterminated string in:", repr(self.text)
                        )
                elif self[...].isspace() and bc == 0:
                    break
                self += 1
            return self[begin:...]
        while self:
            c = self[...]
            if c in BRACKETS:
                brackets.append(self[...])
            elif c in STRING_QUOTES:
                opening = c
                self += 1
                while self:
                    if self[...] == opening:
                        break
                    elif self[...] == "\\":
                        self += 2
                    else:
                        self += 1
                else:
                    raise Exception("unterminated string in:", repr(self.text))
            elif c in BRACKETS.values():
                if len(brackets) > 0 and BRACKETS[brackets[-1]] == c:
                    brackets.pop()
                else:
                    raise Exception(
                        f"unmatched {c!r} at {int(self)}: {self.text!r}"
                    )
            elif len(brackets) == 0 and c.isspace():
                break
            self += 1
        return self[begin:...]

    def parse_next_enum(self) -> "tuple[str, tuple[str, str]]":
        """Next enumerator."""
        self.skip_spaces()
        self += len("!enum ")
        self.skip_spaces()
        b = self.copy()
        while self:
            if self[...] not in VARNAME:
                if self[...] != ":":
                    raise Exception(
                        "unrecognised symbol in after enum object name",
                        self,
                    )
                break
            self += 1
        else:
            raise Exception("unterminated enum first field\n" + repr(self))
        obj = self.text[b:self]
        self += 1
        b = self.copy()
        b += 1
        nc = 0
        while self:
            if self[...] == ")":
                break
            elif self[...] == ",":
                nc += 1
                if nc > 1:
                    raise Exception(
                        "too many fields after enum object\n" + repr(self)
                    )
            self += 1
        else:
            raise Exception("Unterminated enum second field\n" + repr(self))
        alias = tuple(map(str.strip, self[b:...].split(",")))
        self += 1  # skip ending bracket
        return Template.Item(
            type=TagType.SPECIAL, name="enum", args=(obj, alias)
        )

    def parse_next_special(self):
        if self[...:].startswith("!if"):
            return self.parse_next_if()
        elif self[...:].startswith("!enum"):
            return self.parse_next_enum()
        else:
            raise ValueError(
                "unexpected special tag", self[self.idx : self.idx + 5] + "..."
            )

    def parse_next_if(self) -> "tuple[str, tuple[str, str]]":
        """Return next if statements parts."""
        self += len("!if")
        self.skip_spaces()
        b = self.copy()

        while self and self[...] != "\n":
            self += 1

        return Template.Item(
            type=TagType.SPECIAL, name="if", args=(self[b:...],)
        )

    @property
    def row(self) -> int:
        """Find the current position row."""
        return self.text[: self.idx].count("\n") + 1

    @row.setter
    def row(self, val: int):
        col = self.col
        self.idx = 0
        while self.row < val:
            self.idx += 1
        self.col += col

    @property
    def col(self) -> int:
        """Find the actual state column."""
        lines = self.text[: self.idx].splitlines()
        if len(lines) > 0:
            return len(lines[-1])
        else:
            return 0

    @col.setter
    def col(self, val: int) -> bool:
        if len(self.text.splitlines()[self.row - 1]) < val:
            self.idx += val - self.col
            return True
        else:
            return False

    def parse_next_instruction(self) -> "tuple[int, Template.Item]":
        """Parse the next instruction."""
        indent = self.skip_spaces()
        while self and self[...] in "#\n":
            if not self.next_line():
                return
            indent = self.skip_spaces()
        if not self:
            return
        char = self[...]
        if char == "\\":  # a tag
            return indent, self.parse_next_tag()
        elif char == "!":
            return indent, self.parse_next_special()
        else:
            raise ValueError(char)

    def parse_next_tag(self) -> None:
        """Return next tag."""
        name, alias = self.next_tag_name()
        attrs = {}
        while self:
            self.skip_spaces()
            if self[...] == "#":
                break
            key, val = self.next_attr_value()
            if key:
                attrs[key] = val
            self.skip_spaces()
            if not self or self[...] == "\n":
                self.next_line()
                break

        return Template.Item(type=TagType.TAG, name=name, args=(alias, attrs))

    @property
    def line(self) -> str:
        """Get the full current line."""
        return self.text.splitlines()[self.row - 1]

    def __repr__(self):
        """Reproduce the state."""
        return "State(%d) {\n    %s\n    %s\n}" % (
            self.row,
            self.line,
            " " * self.col + "^",
        )

    def parse(self) -> "Template.Item":
        """Parse the state content."""
        tags = []
        while self:
            cmd = self.parse_next_instruction()
            if cmd is not None:
                tags.append(cmd)
        if len(tags) == 0:
            return None
        else:
            last_indent, root = tags[0]
            tree = []
            last_tag = root
            for indent, child in tags[1:]:
                if indent > last_indent:
                    tree.append((last_indent, last_tag))
                elif indent < last_indent:
                    while indent <= tree[-1][0]:
                        tree.pop()
                tree[-1][1].children.append(child)
                child.parent = tree[-1][1]
                last_indent = indent
                last_tag = child
            return root


def evaluate_literal(
    string: str, namespace: Optional[writeable.Namespace] = None
) -> tuple[bool, Any]:
    """Evaluate a litteral from string and optional namespace."""
    from . import media
    from . import constants

    def calls():
        return eval(string[2:-2], {}, namespace)

    string_set = set(string)
    if len(string) > 1:
        b, *_, e = string
    elif len(string) == 1:
        b, e = string, None
    else:
        raise ValueError("empty literal string")
    if hasattr(constants, string):
        return (False, getattr(constants, string))
    elif string == "None":
        return (False, None)
    elif string == "True":
        return (False, True)
    elif string == "False":
        return (False, False)
    elif b == "<" and e == ">":
        return (False, media.get_media(string[1:-1]))
    elif len(string_set - INT) == 0:
        return (False, int(string))
    elif len(string_set - DECIMAL) == 0:
        return Decimal(string)
    elif b == "{" and e == "}":
        if namespace is None:
            raise ValueError(
                "Unallowed writeable.Writeable in none namespaced context",
                string,
            )
        code = string[1:-1]
        if len(code) >= 2 and code[0] == "{" and code[-1] == "}":
            return (False, calls)
        else:
            return (False, eval(code, {}, namespace))
    elif b == "$":
        if len(string) < 2:
            raise Exception(f"Wrong subscription {string!r}")
        typ = string[1]
        if typ == "{":  # Custom writeable
            code = string[2:-1]
            if "||" in code:
                get, set_ = code.split("||")
            else:
                get, set_ = code, ""
            return (
                True,
                writeable.Writeable.from_get_set(namespace, get, set_),
            )
        elif typ == "(":
            return (True, eval(string[2:1]))
        else:
            return (True, writeable.Writeable.from_name(namespace, string[1:]))
    elif b in STRING_QUOTES:
        if e == b:
            return (False, string[1:-1])
        else:
            raise ValueError("Unterminated string:", string)
    elif string[0] == string[-1] == "/":
        return (False, Path(os.path.expandvars(string[1:-1])))
    elif b == "@":
        return (True, dictionary.Translation(string[1:]))
    elif ":" in string and len(string_set - (DECIMAL | SLICE)) == 0:
        if len(d := (string_set - SLICE)) > 0:
            raise ValueError("wrong slice", string, d)
        else:
            return slice(*map(int, string.split(":")))
    elif len(string_set - POINT) == 0:
        values = []
        pos = 0
        while pos < len(string):
            begin = pos
            if "," in string[pos:]:
                end = string.index(",", pos)
            else:
                end = len(string)
            try:
                if "." in string[begin:end]:
                    dec = Decimal(string[begin:end])
                else:
                    dec = int(string[begin:end])
            except decimal.InvalidOperation as e:
                raise ValueError(
                    str(e),
                    string,
                    begin,
                    string[begin:end],
                ) from e
            else:
                values.append(dec)
            finally:
                pos = end + 1
        return (False, tuple(values))
    else:
        raise ValueError("Unrecognsed literal:", repr(string))


class Template:
    """
    A taktk component template, can be renderred into a real component.
    Holds parsed instructions and namespace.
    """

    @dataclasses.dataclass
    class Item:
        """
        Item in template parse result, represents an instruction or tag.
        """

        type: TagType
        name: str
        args: tuple
        parent: "Template.Item" = None
        children: list = dataclasses.field(default_factory=list)

        def render(self, parent, namespace):
            """Create the component."""

            if self.type is TagType.TAG:
                alias, attrs = self.args
                comp = get_component(self.name, namespace)(
                    parent=parent,
                    attrs=attrs,
                    namespace=namespace,
                )
                if alias is not None:
                    namespace[alias] = comp
                for child in self.children:
                    child.render(comp, namespace)
                return comp
            elif self.type is TagType.SPECIAL:
                if self.name == "if":
                    return component.IfComponent(
                        self.args[0], namespace, parent, self.children.copy()
                    )
                elif self.name == "enum":
                    return component.EnumComponent(
                        self.args[0],
                        self.args[1],
                        namespace,
                        parent,
                        self.children.copy(),
                    )
                else:
                    raise ValueError(f"Unknown special {self.name}")
            else:
                raise NotImplementedError(f"Unimplemented tagtype {self.type}")

        def __repr__(self) -> str:
            """Reproduce the object as string"""
            head = self.name
            children = ""
            if self.type == TagType.TAG:
                alias, attrs = self.args
                if alias is not None:
                    head += ":" + alias
                if attrs:
                    head += "(" + " ".join(map("=".join, attrs.items())) + ")"
            if len(self.children) > 0:
                children = (
                    "{\n"
                    + "\n".join(
                        [
                            "  " + ln
                            for ln in ",\n".join(
                                map(Template.Item.__repr__, self.children)
                            ).splitlines()
                        ]
                    )
                    + "\n}"
                )
            return f"{head}{children}"

    instructions: list[Item]

    def __init__(self, root: Item, namespace=None):
        """Create a taktl template"""
        self.root = root
        self.namespace = namespace

    @classmethod
    def parse(cls, string: str) -> "Template":
        """Load template from taktl source string."""
        return Template(State(string.replace("\\\n", "")).parse())

    def eval(self, _namespace: Optional[writeable.Namespace] = None):
        """Evaluate the template in the given namespace."""
        namespace = self.namespace or _namespace
        assert namespace is not None, "No namespace specified!"

        return self.root.render(None, namespace)

    def __repr__(self) -> str:
        return str(self.root)


def get_component(
    name: str, namespace: Optional[writeable.Namespace] = None
) -> "component.BaseComponent":
    """Get a component by name from builtins or optional `namespace`."""
    from . import components

    try:
        return eval(name, {}, (namespace.vars or {}) | vars(components))
    except NameError as e:
        raise NameError(f"Component {name!r} does not exist.") from e
