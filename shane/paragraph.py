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

from enum import Enum


class PType(Enum):
    """Enum for paragraph types."""

    SCENE = 0
    ACTION = 1
    NAME = 2
    PARENTHETICALS = 3
    DIALOG = 4


class PPrefs(object):
    """Enum for paragraph preferences."""

    SCENE_INDENT = 0
    SCENE_WIDTH = 60
    SCENE_PREC_EMPTY = 2
    SCENE_ENTER = PType.ACTION
    SCENE_TAB = PType.ACTION

    ACTION_INDENT = 0
    ACTION_WIDTH = 60
    ACTION_PREC_EMPTY = 1
    ACTION_ENTER = PType.ACTION
    ACTION_TAB = PType.NAME

    NAME_INDENT = 25
    NAME_WIDTH = 35
    NAME_PREC_EMPTY = 1
    NAME_ENTER = PType.DIALOG
    NAME_TAB = PType.ACTION

    PARENT_INDENT = 20
    PARENT_WIDTH = 15
    PARENT_PREC_EMPTY = 0
    PARENT_ENTER = PType.DIALOG
    PARENT_TAB = PType.DIALOG

    DIALOG_INDENT = 15
    DIALOG_WIDTH = 35
    DIALOG_PREC_EMPTY = 0
    DIALOG_ENTER = PType.NAME
    DIALOG_TAB = PType.PARENTHETICALS

    @staticmethod
    def get_indent(ptype: PType) -> int:
        """Return indentation of paragraph type."""
        if ptype == PType.SCENE:
            return PPrefs.SCENE_INDENT
        elif ptype == PType.ACTION:
            return PPrefs.ACTION_INDENT
        elif ptype == PType.NAME:
            return PPrefs.NAME_INDENT
        elif ptype == PType.PARENTHETICALS:
            return PPrefs.PARENT_INDENT
        else:
            return PPrefs.DIALOG_INDENT

    @staticmethod
    def get_width(ptype: PType) -> int:
        """Return width of paragraph type."""
        if ptype == PType.SCENE:
            return PPrefs.SCENE_WIDTH
        elif ptype == PType.ACTION:
            return PPrefs.ACTION_WIDTH
        elif ptype == PType.NAME:
            return PPrefs.NAME_WIDTH
        elif ptype == PType.PARENTHETICALS:
            return PPrefs.PARENT_WIDTH
        else:
            return PPrefs.DIALOG_WIDTH

    @staticmethod
    def get_prec_empty(ptype: PType) -> int:
        """Return preceding empty lines of paragraph type."""
        if ptype == PType.SCENE:
            return PPrefs.SCENE_PREC_EMPTY
        elif ptype == PType.ACTION:
            return PPrefs.ACTION_PREC_EMPTY
        elif ptype == PType.NAME:
            return PPrefs.NAME_PREC_EMPTY
        elif ptype == PType.PARENTHETICALS:
            return PPrefs.PARENT_PREC_EMPTY
        else:
            return PPrefs.DIALOG_PREC_EMPTY

    @staticmethod
    def get_enter(ptype: PType) -> PType:
        """Return paragraph type to come after typing enter in a paragraph."""
        if ptype == PType.SCENE:
            return PPrefs.SCENE_ENTER
        elif ptype == PType.ACTION:
            return PPrefs.ACTION_ENTER
        elif ptype == PType.NAME:
            return PPrefs.NAME_ENTER
        elif ptype == PType.PARENTHETICALS:
            return PPrefs.PARENT_ENTER
        else:
            return PPrefs.DIALOG_ENTER

    @staticmethod
    def get_tab(ptype: PType) -> PType:
        """Return paragraph type to convert to from paragraph type."""
        if ptype == PType.SCENE:
            return PPrefs.SCENE_TAB
        elif ptype == PType.ACTION:
            return PPrefs.ACTION_TAB
        elif ptype == PType.NAME:
            return PPrefs.NAME_TAB
        elif ptype == PType.PARENTHETICALS:
            return PPrefs.PARENT_TAB
        else:
            return PPrefs.DIALOG_TAB


class Paragraph(object):
    """A paragraph in a screenplay."""

    def __init__(self, ptype: PType, text=None):
        """Initialize paragraph with type and optionally text."""
        if not text:
            text = "\0"
        elif len(text) == 0 or text[-1] != "\0":
            text += "\0"

        self._ptype = ptype
        self._text = text
        self._lines = [1]
        self._line_count = 1 + PPrefs.get_prec_empty(self._ptype)

        self._reformat()

    def _reformat(self):
        """Reformat paragraph calculating line wraps."""
        width = PPrefs.get_width(self._ptype)

        self._lines.clear()
        self._lines.append(0)

        current_word_len = 0

        for char in self._text:
            current_word_len += 1

            # TODO work with hyphen
            if char == ' ' or char == '\0':
                self._lines[-1] += current_word_len
                current_word_len = 0
            elif current_word_len == width:
                self._lines[-1] += current_word_len
                self._lines.append(0)
                current_word_len = 0
            elif self._lines[-1] + current_word_len > width:
                self._lines.append(0)

        self._line_count = len(self._lines) + PPrefs.get_prec_empty(self._ptype)

    def sp_input(self, pos: int, text: str):
        """Input text into paragraph."""
        self._text = self._text[:pos] + text + self._text[pos:]
        self._reformat()

    def sp_delete(self, pos: int, length: int) -> str:
        """Delete text from paragraph and return deleted text."""
        deleted = self._text[pos:pos + length]
        self._text = self._text[:pos] + self._text[pos + length:]
        self._reformat()
        return deleted

    def sp_set_type(self, ptype: PType):
        """Set paragraph's type."""
        self._ptype = ptype
        self._reformat()

    def get_text(self) -> str:
        """Return paragraph's text (ending with null character)."""
        return self._text

    def get_line_count(self) -> int:
        """Return number of lines."""
        return self._line_count

    def get_lines(self) -> list():
        """Return text in line wrapped form."""
        result = []

        for i in range(PPrefs.get_prec_empty(self._ptype)):
            result.append("")

        line_start = 0
        for line_len in self._lines:
            result.append(self._text[line_start: line_start + line_len])
            line_start += line_len

        return result

    def get_line_column_at_pos(self, pos: int) -> (int, int):
        """Return line and column for position."""
        line = 0
        for i in range(0, len(self._lines)):
            if pos - self._lines[i] >= 0:
                pos -= self._lines[i]
                line += 1
            else:
                break

        return line + PPrefs.get_prec_empty(self._ptype), pos

    def get_pos_at_line_column(self, line: int, column: int) -> int:
        """Return position for column in line."""
        line_count = len(self._lines)
        line -= PPrefs.get_prec_empty(self._ptype)
        if line < 0:
            return -1
        elif line >= line_count:
            return -2

        if column < 0:
            column = 0
        if column >= self._lines[line]:
            column = self._lines[line] - 1

        for i in range(line):
            column += self._lines[i]

        return column

    def get_type(self):
        """Return type."""
        return self._ptype

    def __str__(self) -> PType:
        """Return as string."""
        result = ""
        indent = " " * PPrefs.get_indent(self._ptype)
        for line in self.get_lines():
            result += indent + line + "\n"
        return result
