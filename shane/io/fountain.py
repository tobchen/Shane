# coding=utf-8

# Shane - a poor man and/or hipster's TUI screenwriting software
# Copyright (C) 2016 Tobias Heukäufer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import shutil
import tempfile
from enum import Enum

from shane.paragraph import Paragraph, PType


class _PrevState(Enum):
    """Enum for recording the previous line's type in fountain script."""

    EMPTY = 0
    SCENE_HINT = 1
    NAME_HINT = 2
    SCENE_AND_NAME_HINT = 3
    PARENT = 4
    DIALOG = 5
    ACTION = 6


def _is_scene_conform(line: str):
    """Return if a line is scene conform (disregarding scene forcing)."""
    return line.lower().startswith(("int ", "ext ", "est ", "int./ext ",
                                    "int/ext ", "i/e ", "int.", "ext.", "est.",
                                    "int./ext.", "int/ext.", "i/e."))


def _is_name_conform(line: str):
    """Return if a line is name conform (disregarding name forcing)."""
    has_at_least_one_alphabetical = False
    for char in line:
        if 65 <= ord(char) <= 90 or 97 <= ord(char) <= 122:
            has_at_least_one_alphabetical = True
            break
    return has_at_least_one_alphabetical and\
        line.split("(")[0].isupper() and\
        not line.startswith("!")


def _hint_scene(line: str):
    """Return if a line is scene conform (including scene forcing)."""
    return line.lower().startswith(".") or _is_scene_conform(line)


def _hint_name(line: str):
    """Return if a line is name conform (including name forcing)."""
    return line.startswith("@") or _is_name_conform(line)


def _hint_parenthetical(line: str):
    """Return if a line is parentheticals conform."""
    return len(line) >= 2 and line[0] == "(" and line[-1] == ")"


def _append_scene(plist, line):
    """Append a scene to a paragraph list."""
    if line.startswith("."):
        line = line[1:]
    plist.append(Paragraph(PType.SCENE, line))


def _append_action(plist, line):
    """Append an action to a paragraph list."""
    if line.startswith("!"):
        line = line[1:]
    plist.append(Paragraph(PType.ACTION, line))


def _append_name(plist, line):
    """Append a name to a paragraph list."""
    if line.startswith("@"):
        line = line[1:]
    plist.append(Paragraph(PType.NAME, line))


def _append_parent(plist, line):
    """Append parentheticals to a paragraph list."""
    plist.append(Paragraph(PType.PARENTHETICALS, line[1:-1]))


def read(path: str):
    """Read fountain script from path."""
    result = []

    with open(path, "r") as file:
        prev_state = _PrevState.EMPTY
        prev_line = ""

        for line in file:
            line = line.strip()

            if prev_state == _PrevState.EMPTY:
                if line:
                    scene_hint = _hint_scene(line)
                    name_hint = _hint_name(line)
                    if scene_hint and name_hint:
                        prev_state = _PrevState.SCENE_AND_NAME_HINT
                    elif scene_hint:
                        prev_state = _PrevState.SCENE_HINT
                    elif name_hint:
                        prev_state = _PrevState.NAME_HINT
                    else:
                        _append_action(result, line)
                        prev_state = _PrevState.ACTION
            elif prev_state == _PrevState.SCENE_HINT:
                if not line:
                    _append_scene(result, prev_line)
                    prev_state = _PrevState.EMPTY
                else:
                    _append_action(result, prev_line)
                    _append_action(result, line)
                    prev_state = _PrevState.ACTION
            elif prev_state == _PrevState.NAME_HINT:
                if line:
                    _append_name(result, prev_line)
                    if _hint_parenthetical(line):
                        _append_parent(result, line)
                        prev_state = _PrevState.PARENT
                    else:
                        result.append(Paragraph(PType.DIALOG, line))
                        prev_state = _PrevState.DIALOG
                else:
                    _append_action(result, prev_line)
                    prev_state = _PrevState.EMPTY
            elif prev_state == _PrevState.SCENE_AND_NAME_HINT:
                if line:
                    result.append(Paragraph(PType.NAME, prev_line))
                    if _hint_parenthetical(line):
                        _append_parent(result, line)
                        prev_state = _PrevState.PARENT
                    else:
                        result.append(Paragraph(PType.DIALOG, line))
                        prev_state = _PrevState.DIALOG
                else:
                    _append_scene(result, prev_line)
                    prev_state = _PrevState.EMPTY
            elif prev_state == _PrevState.PARENT:
                if line:
                    result.append(Paragraph(PType.DIALOG, line))
                    prev_state = _PrevState.DIALOG
                else:
                    prev_state = _PrevState.EMPTY
            elif prev_state == _PrevState.DIALOG:
                if line:
                    if _hint_parenthetical(line):
                        _append_parent(result, line)
                        prev_state = _PrevState.PARENT
                    else:
                        paragraph = result[-1]
                        paragraph.sp_input(len(paragraph.get_text()) - 1,
                                           line)
                        prev_state = _PrevState.DIALOG
                else:
                    prev_state = _PrevState.EMPTY
            elif prev_state == _PrevState.ACTION:
                if line:
                    _append_action(result, line)
                    prev_state = _PrevState.ACTION
                else:
                    prev_state = _PrevState.EMPTY

            prev_line = line

        if prev_state == _PrevState.SCENE_HINT:
            _append_scene(result, prev_line)
        elif prev_state == _PrevState.NAME_HINT:
            _append_name(result, prev_line)
        elif prev_state == _PrevState.SCENE_AND_NAME_HINT:
            if '.' in prev_line:
                result.append(Paragraph(PType.SCENE, prev_line))
            else:
                result.append(Paragraph(PType.NAME, prev_line))

    return result


def write(path, paragraphs):
    """Save fountain script to path."""
    file, tmp_path = tempfile.mkstemp()

    prev_empty = False
    for par in paragraphs:
        line = par.get_text()[:-1]
        ptype = par.get_type()

        do_prev_empty = False
        do_next_empty = False

        if ptype == PType.SCENE:
            if not _is_scene_conform(line):
                line = "." + line
            do_prev_empty = do_next_empty = True
        elif ptype == PType.ACTION:
            if _is_scene_conform(line) or _is_name_conform(line) or\
                    _hint_parenthetical(line):
                line = "!" + line
            do_prev_empty = do_next_empty = True
        elif ptype == PType.NAME:
            if not _is_name_conform(line):
                line = "@" + line
            do_prev_empty = True
        elif ptype == PType.PARENTHETICALS:
            line = "(" + line + ")"

        if not prev_empty and do_prev_empty:
            os.write(file, "\n".encode())
        os.write(file, (line + "\n").encode())
        if do_next_empty:
            os.write(file, "\n".encode())

        prev_empty = do_next_empty

    os.close(file)

    shutil.copy(tmp_path, path)
    os.remove(tmp_path)
