"""
The main components parser

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

import string
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from pyoload import annotate

from ..dictionary import Translation
from ..writeable import Expression
from ..writeable import NamespaceWriteable

SPACE = frozenset(" ")
VARNAME = frozenset(string.ascii_letters + string.digits + "_")
COMPONENT_NAME = VARNAME | frozenset(".")
BRACKETS = dict(map(tuple, "(),[],{}".split(",")))
STRING_QUOTES = frozenset("\"'")
INT = frozenset(string.digits)
DECIMAL = frozenset(string.digits + ".")
SLICE = INT | frozenset(":")
POINT = DECIMAL | frozenset(",")
ATTR_NAME = frozenset(':') | VARNAME


class State:
    __slots__ = ("text", "idx")
    text: str
    idx: int

    @annotate
    def __init__(self, text: str, idx: int = 0):
        self.text = text
        self.idx = idx

    def __ior__(self, other: "State"):
        if not isinstance(other, State):
            return NotImplemented
        self.idx = other.idx
        return self

    def copy(self):
        return State(text=self.text, idx=self.idx)

    def __setattr__(self, attr, val):
        if attr == "text" and hasattr(self, "text"):
            raise NotImplementedError()
        else:
            super().__setattr__(attr, val)

    def __int__(self):
        return self.idx

    def __index__(self):
        return self.idx

    def __iadd__(self, val):
        self.idx += val
        return self

    def __add__(self, val):
        return self.idx + val

    def __radd__(self, val):
        return self.idx + val

    def __gt__(self, val):
        return int.__gt__(self.idx, val)

    def __lt__(self, val):
        return int.__lt__(self.idx, val)

    def __hash__(self):
        return self.idx

    def __repr__(self):
        return f"<State:{self.idx}>"

    def __len__(self):
        return len(self.text)

    def __getitem__(self, item):
        if item == ...:
            return self.text[self:]
        else:
            return self.text.__getitem__(item)

    def __bool__(self):
        return self.idx < len(self.text)


@annotate
def skip_spaces(_state: State) -> State:
    """
    Returns the index of the next non-space character
    """
    state = _state.copy()
    while state < len(state.text) and state.text[state] in SPACE:
        state += 1
    return state


@annotate
def tag_name(_state: State) -> tuple[State, str, Optional[str]]:
    """
    Gets next tag name from `\\` character, may include alias
    """
    begin = _state.copy()
    begin |= skip_spaces(begin)
    state = begin.copy()
    state += 1
    name = ""
    while len(state.text) > state and state.text[state] in COMPONENT_NAME:
        state += 1
    name = state.text[begin + 1 : state]

    if len(state.text) > state and state.text[state] == ":":
        state += 1
        begin = state.copy()
        while (
            len(state.text) > int(state)
            and state.text[int(state)] in COMPONENT_NAME
        ):
            state += 1
        alias = state.text[begin : int(state)]
    else:
        alias = None
    return (state, name, alias)


@annotate
def next_attr_value(_state: State) -> tuple[State, str, str]:
    """
    Gets next attribute value pair from `\\` character, may include alias
    """
    begin = _state.copy()
    begin |= skip_spaces(begin)
    state = begin.copy()

    attr = ""

    while state and state[...][0] in ATTR_NAME:
        attr += state[...][0]
        state += 1
    if not state or state[...][0] != "=":
        state += 1
        # raise Exception(f"missing equal after {attr!r} sign in:", state.text)
        return state, attr, 'True'
    else:
        state += 1
        nstate, val = next_value(state)
        state |= nstate
        return state, attr, val


@annotate
def next_value(_state: State) -> tuple[State, str]:
    """
    Gets next attribute value pair from `\\` character, may include alias
    """
    begin = _state.copy()
    begin |= skip_spaces(begin)
    state = begin.copy()

    val = ""
    brackets = []
    if (
        ":" in state[...]
        and state[...][: (n := state[...].index(":"))].isalpha()
        and len(brackets) == 0
    ):
        begin = state.copy()
        state += n
        bc = 0
        while state:
            if state[...][0] == "{":
                bc += 1
            elif state[...][0] == "}":
                bc -= 1
            elif (quote := state[...][0]) in STRING_QUOTES:
                state += 1
                while state:
                    if state[...][0] == quote:
                        break
                    elif state[...][0] == "\\":
                        state += 2
                    else:
                        state += 1
                else:
                    raise Exception(
                        "unterminated string in:", repr(state.text)
                    )
            elif state[...][0].isspace() and bc == 0:
                break
            state += 1
        return state, state.text[begin:state]
    while state:
        c = state[...][0]
        if c in BRACKETS:
            brackets.append(state[...][0])
        elif c in STRING_QUOTES:
            opening = c
            state += 1
            while state:
                if state[...][0] == opening:
                    break
                elif state[...][0] == "\\":
                    state += 2
                else:
                    state += 1
            else:
                raise Exception("unterminated string in:", repr(state.text))
        elif c in BRACKETS.values():
            if len(brackets) > 0 and BRACKETS[brackets[-1]] == c:
                brackets.pop()
            else:
                raise Exception(
                    f"unmatched {c!r} at {int(state)}: {state.text!r}"
                )
        elif len(brackets) == 0 and c.isspace():
            break
        state += 1
    return state, state.text[begin:state]


@annotate
def next_enum(_state: State) -> tuple[State, str, tuple[str, str]]:
    """
    Gets next attribute value pair from `\\` character, may include alias
    """
    begin = _state.copy()
    begin |= skip_spaces(begin)
    state = begin.copy()
    state += len("!enum ")
    state |= skip_spaces(state)
    b = state.copy()
    while state:
        if state[...][0] not in VARNAME:
            if state[...][0] != ":":
                raise Exception(
                    "unrecognised symbol in after enum object name", state.text
                )
            break
        state += 1
    else:
        raise Exception("unterminated enum first field", state.text)
    obj = state.text[b:state]
    state += 1
    b = state.copy()
    b += 1
    nc = 0
    while state:
        if state[...][0] == ")":
            break
        elif state[...][0] == ",":
            nc += 1
            if nc > 1:
                raise Exception(
                    "too many fields after enum object", state.text
                )
        state += 1
    else:
        raise Exception("Unterminated enum second field", state.text)
    alias = tuple(map(str.strip, state[b:state].split(",")))
    return state, obj, alias


@annotate
def next_if(_state: State) -> tuple[State, str, tuple[str, str]]:
    """
    Gets next attribute value pair from `\\` character, may include alias
    """
    begin = _state.copy()
    begin |= skip_spaces(begin)
    state = begin.copy()
    state += len("!if ")
    state |= skip_spaces(state)
    b = state.copy()

    while state and state[...][0] != "\n":
        state += 1

    return state, state.text[b:state]


@annotate
def evaluate_literal(string: str, namespace: "Optional[Namespace]" = None):
    from ..media import get_media
    import tkinter.constants

    string_set = set(string)
    if len(string) > 1:
        b, *_, e = string
    elif len(string) == 1:
        b, e = string, None
    else:
        raise ValueError("empty literal string")
    if string[0] == "!":
        auto_eval = True
        aes_string = string[1:]
    else:
        auto_eval = False
        aes_string = string
    if hasattr(tkinter.constants, string):
        return getattr(tkinter.constants, string)
    elif string == "None":
        return None
    elif string == "True":
        return True
    elif string == "False":
        return False
    elif ":" in string and string[: string.index(":")].isalpha():
        return get_media(string)
    elif len(string_set - INT) == 0 and string.isnumeric():
        return int(string)
    elif len(string_set - DECIMAL) == 0:
        return Decimal(string)
    elif (
        len(aes_string) > 2 and aes_string[0] == "{" and aes_string[-1] == "}"
    ):
        if namespace is None:
            raise ValueError(
                "Unallowed Writeable in none namespaced context", string
            )
        st = aes_string[1:-1]
        if len(st) >= 2 and st[0] == "{" and st[-1] == "}":
            if auto_eval:
                return NamespaceWriteable(namespace, st[1:-1]).get()
            else:
                return NamespaceWriteable(namespace, st[1:-1])
        else:
            if auto_eval:
                return Expression(namespace, st).get()
            else:
                return Expression(namespace, st)
    elif b in STRING_QUOTES:
        if e == b:
            return string[1:-1]
        else:
            raise ValueError("Unterminated string:", string)
    elif string[0] == string[-1] == "/":
        return Path(os.path.expandvars(string[1:-1]))
    elif string[0] == "[" and string[-1] == "]":
        return Translation(string[1:-1])
    elif ":" in string and len(string_set - (NUMBER | SLICE)) == 0:
        if len(d := (string_set - SLICE)) > 0:
            idx = pos + min(string.index(t) for t in d)
            raise ValueError(
                "wrong slice",
                string,
            )
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
                raise WrongLiteral(
                    str(e),
                    full_string,
                    begin,
                    string[begin:end],
                ) from e
            else:
                values.append(dec)
            finally:
                pos = end + 1
        return tuple(values)
    else:
        raise ValueError("Unrecognsed literal:", repr(string))


from . import _Component
from .instructions import Namespace
