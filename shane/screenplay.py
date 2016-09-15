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

import time

from shane.io import fountain
from shane.paragraph import Paragraph, PType, PPrefs


class NameDB(object):
    """Name database for a screenplay to store and retrieve names."""

    def __init__(self):
        """Initialize the name database."""
        self._a_m = []
        self._n_z = []
        self._else = []

    def clear(self):
        """Clear the database's contents."""
        self._a_m.clear()
        self._n_z.clear()
        self._else.clear()

    def add(self, name: str):
        """Add a name to the database."""
        if not name:
            return

        first_char = ord(name[0].lower())
        list_to_add_to = self._else
        if 97 <= first_char <= 109:
            list_to_add_to = self._a_m
        elif 110 <= first_char <= 122:
            list_to_add_to = self._n_z

        for i in range(len(list_to_add_to)):
            if name == list_to_add_to[i]:
                break
            elif name < list_to_add_to[i]:
                list_to_add_to.insert(i, name)
                break
        else:
            list_to_add_to.append(name)

    def get_next(self, name: str, starting_with: str) -> str:
        """Get a name from the database based on a name's beginning."""
        if not starting_with:
            return name

        first_char = ord(starting_with[0].lower())
        list_to_go_from = self._else
        if 97 <= first_char <= 109:
            list_to_go_from = self._a_m
        elif 110 <= first_char <= 122:
            list_to_go_from = self._n_z

        proposals = [n for n in list_to_go_from if n.startswith(starting_with)]
        try:
            index = proposals.index(name)
            if index < len(proposals) - 1:
                return proposals[index + 1]
            else:
                return proposals[0]
        except ValueError:
            if len(proposals) > 0:
                return proposals[0]
            else:
                return name


class ActionBundle(object):
    """A bundle of actions remembering when last action was inserted."""

    # 200ms
    TIME_DISTANCE = 0.2

    def __init__(self, action):
        """Initialize the bundle with a new action."""
        self.actions = [action]
        self.last_action = time.time()

    def is_relatively_new(self):
        """Return if not much time has passed since last action addition."""
        return time.time() - self.last_action < ActionBundle.TIME_DISTANCE

    def add_action(self, action):
        """Add new action."""
        self.actions.insert(0, action)
        self.last_action = time.time()


class InputAction(object):
    """Action for text input."""
    def __init__(self, pindex: int, position: int, text: str):
        """Initialize action."""
        self.pindex = pindex
        self.position = position
        self.text = text


class DeleteAction(object):
    """Action for text deletion."""
    def __init__(self, pindex: int, position: int, text: str):
        """Initialize action."""
        self.pindex = pindex
        self.position = position
        self.text = text


class NewParagraphAction(object):
    """Action for paragraph creation."""
    def __init__(self, pindex: int, ptype: PType, text: str):
        """Initialize action."""
        self.pindex = pindex
        self.ptype = ptype
        self.text = text


class DeleteParagraphAction(object):
    """Action for paragraph deletion."""
    def __init__(self, pindex: int, ptype: PType, text: str):
        """Initialize action."""
        self.pindex = pindex
        self.ptype = ptype
        self.text = text


class ChangePTypeAction(object):
    """Action for paragraph type change."""
    def __init__(self, pindex: int, prev_type: PType, new_type: PType):
        """Initialize action."""
        self.pindex = pindex
        self.prev_type = prev_type
        self.new_type = new_type


class Screenplay(object):
    """A screenplay."""

    # Why 20? Dunno.
    MAX_ACTION_SIZE = 20

    def __init__(self, path: str=None):
        """Initialize the screenplay."""
        self._paragraphs = []

        self._path = path
        if self._path:
            try:
                self._paragraphs.extend(fountain.read(path))
            except OSError:
                pass
        if not path or len(self._paragraphs) == 0:
            self._paragraphs.append(Paragraph(PType.SCENE))

        self._cursor_par = 0
        self._cursor_pos = 0

        self._name_db = NameDB()
        self.do_rebuild_autocomplete_db()

        # First action is newest action
        self._previous_actions = []
        self._current_action = 0

    # HERE COME THE ONLY METHODS ALLOWED TO USE PARAGRAPH'S SP_-METHODS OR
    # CHANGE SELF._PARAGRAPHS

    def _input(self, pindex: int, position: int, text: str, undo: bool=True):
        """Input text into a paragraph."""
        self._paragraphs[pindex].sp_input(position, text)
        if undo:
            self._add_action(InputAction(pindex, position, text))

    def _delete(self, pindex: int, position: int, length: int, undo: bool=True) -> str:
        """Delete text from a pragraph and return deleted text."""
        deleted = self._paragraphs[pindex].sp_delete(position, length)
        if undo:
            self._add_action(DeleteAction(pindex, position, deleted))
        return deleted

    def _new_paragraph(self, pindex: int, ptype: PType, text: str=None, undo: bool=True):
        """Add a new paragraph at index."""
        self._paragraphs.insert(pindex, Paragraph(ptype, text))
        if undo:
            self._add_action(NewParagraphAction(pindex, ptype, text))

    def _delete_paragraph(self, pindex: int, undo: bool=True):
        """Delete paragraph at index."""
        text = self._paragraphs[pindex].get_text()[:-1]
        ptype = self._paragraphs[pindex].get_type()
        self._paragraphs.pop(pindex)
        if undo:
            self._add_action(DeleteParagraphAction(pindex, ptype, text))

    def _change_paragraph_type(self, pindex: int, ptype: PType, undo: bool=True):
        """Change given paragraph's type at index."""
        prev_type = self._paragraphs[pindex].get_type()
        self._paragraphs[pindex].sp_set_type(ptype)
        if undo:
            self._add_action(ChangePTypeAction(pindex, prev_type, ptype))

    # HERE COME METHODS ONLY TO BE USED BY METHODS FROM PREVIOUS BLOCK

    def _add_action(self, action):
        """Add action to previous actions list."""
        if len(self._previous_actions) > 0 and self._current_action > 0:
            self._previous_actions = \
                self._previous_actions[self._current_action:]
        self._current_action = 0

        if len(self._previous_actions) > 0 and\
                self._previous_actions[0].is_relatively_new():
            self._previous_actions[0].add_action(action)
        else:
            self._previous_actions.insert(0, ActionBundle(action))
            if len(self._previous_actions) > Screenplay.MAX_ACTION_SIZE:
                self._previous_actions = \
                    self._previous_actions[:Screenplay.MAX_ACTION_SIZE]

    # OKAY, THANKS FOR YOUR UNDERSTANDING, YOU CAN GO BACK TO YOUR STUFF

    def do_input(self, text: str):
        """Input text at cursor position."""
        text = text.split("\n")
        self._input(self._cursor_par, self._cursor_pos, text[0])
        self._cursor_pos += len(text[0])

        # Oh noes, there were newlines in input text!
        if len(text) > 1:
            cur_par = self._paragraphs[self._cursor_par]

            removed = self._delete(self._cursor_par, self._cursor_pos,
                                   len(cur_par.get_text()) -
                                   self._cursor_pos - 1)
            for line in text[1:]:
                prev_par = self._cursor_par
                self._cursor_par += 1
                self._new_paragraph(self._cursor_par,
                                    PPrefs.get_enter(
                                        self._paragraphs[prev_par].get_type()),
                                    line)
            self._cursor_pos = len(text[-1])
            self._input(self._cursor_par, self._cursor_pos, removed)

    def do_delete_backward(self):
        """Delete one character backwards from cursor position."""
        if not self._cursor_par == self._cursor_pos == 0:
            self.do_move_cursor_left()
            self.do_delete_forward()

    def do_delete_forward(self):
        """Delete one character forwards from cursor position."""
        cur_par = self._paragraphs[self._cursor_par]
        if self._cursor_pos < len(cur_par.get_text()) - 1:
            self._delete(self._cursor_par, self._cursor_pos, 1)
        elif self._cursor_par < len(self._paragraphs) - 1:
            self._input(self._cursor_par, self._cursor_pos,
                        self._paragraphs[self._cursor_par + 1].get_text()[:-1])
            self._delete_paragraph(self._cursor_par + 1)

    def do_autocomplete_name(self):
        """Autocomplete name at cursor position."""
        cur_par = self._paragraphs[self._cursor_par]
        if cur_par.get_type() != PType.NAME:
            return
        cur_name = cur_par.get_text()[:-1]
        proposal = self._name_db.get_next(cur_name,
                                          cur_name[:self._cursor_pos])
        self._delete(self._cursor_par, 0, len(cur_name))
        self._input(self._cursor_par, 0, proposal)

    def do_convert_tab_style(self):
        """Convert paragraph at cursor position according to tab convention."""
        self._change_paragraph_type(self._cursor_par, PPrefs.get_tab(
            self._paragraphs[self._cursor_par].get_type()))

    def do_convert_to_prev_ptype(self):
        """Convert paragraph at cursor position to previous type in order."""
        ptypes = list(PType.__iter__())
        index = ptypes.index(self._paragraphs[self._cursor_par].get_type()) - 1
        self._change_paragraph_type(self._cursor_par, ptypes[index])

    def do_convert_to_next_ptype(self):
        """Convert paragraph at cursor position to next type in order."""
        ptypes = list(PType.__iter__())
        index = ptypes.index(self._paragraphs[self._cursor_par].get_type()) + 1
        self._change_paragraph_type(self._cursor_par, ptypes[index % len(ptypes)])

    def do_move_cursor_left(self):
        """Move cursor one character backward."""
        if self._cursor_pos > 0:
            self._cursor_pos -= 1
        elif self._cursor_par > 0:
            self._cursor_par -= 1
            self._cursor_pos = \
                len(self._paragraphs[self._cursor_par].get_text()) - 1

    def do_move_cursor_right(self):
        """Move cursor one character forward."""
        if self._cursor_pos \
                < len(self._paragraphs[self._cursor_par].get_text()) - 1:
            self._cursor_pos += 1
        elif self._cursor_par < len(self._paragraphs) - 1:
            self._cursor_pos = 0
            self._cursor_par += 1

    def do_move_cursor_up(self):
        """Move cursor one line upward."""
        cur_par = self._paragraphs[self._cursor_par]
        line, col = cur_par.get_line_column_at_pos(self._cursor_pos)
        line -= 1
        cur_pos_new = cur_par.get_pos_at_line_column(line, col)
        if cur_pos_new >= 0:
            self._cursor_pos = cur_pos_new
        elif self._cursor_par > 0:
            self._cursor_par -= 1
            prev_par = self._paragraphs[self._cursor_par]
            line = prev_par.get_line_count() - 1
            col += PPrefs.get_indent(cur_par.get_type()) \
                - PPrefs.get_indent(prev_par.get_type())
            self._cursor_pos = prev_par.get_pos_at_line_column(line, col)

    def do_move_cursor_down(self):
        """Move cursor one line downward."""
        cur_par = self._paragraphs[self._cursor_par]
        line, col = cur_par.get_line_column_at_pos(self._cursor_pos)
        line += 1
        cur_pos_new = cur_par.get_pos_at_line_column(line, col)
        if cur_pos_new >= 0:
            self._cursor_pos = cur_pos_new
        elif self._cursor_par < len(self._paragraphs) - 1:
            self._cursor_par += 1
            next_par = self._paragraphs[self._cursor_par]
            next_par_type = next_par.get_type()
            line = PPrefs.get_prec_empty(next_par_type)
            col += PPrefs.get_indent(cur_par.get_type()) \
                - PPrefs.get_indent(next_par_type)
            self._cursor_pos = next_par.get_pos_at_line_column(line, col)

    def do_move_cursor_line_start(self):
        """Move cursor to line start (as in Home)."""
        column = self._paragraphs[self._cursor_par].get_line_column_at_pos(
            self._cursor_pos)[1]
        self._cursor_pos -= column

    def do_move_cursor_line_end(self):
        """Move cursor to line and (as in End)."""
        cur_par = self._paragraphs[self._cursor_par]
        line, column = cur_par.get_line_column_at_pos(self._cursor_pos)
        line_length = len(cur_par.get_lines()[line])
        self._cursor_pos += line_length - column - 1

    def do_move_cursor_paragraph_end(self):
        """Move cursor to paragraph end."""
        self._cursor_pos = \
            len(self._paragraphs[self._cursor_par].get_text()) - 1

    def do_move_cursor_prev_scene(self):
        """Move cursor to previous scene heading."""
        for i in range(self._cursor_par - 1, -1, -1):
            if self._paragraphs[i].get_type() == PType.SCENE:
                self._cursor_pos = 0
                self._cursor_par = i
                break
        else:
            for i in range(len(self._paragraphs) - 1, self._cursor_par, -1):
                if self._paragraphs[i].get_type() == PType.SCENE:
                    self._cursor_pos = 0
                    self._cursor_par = i
                    break

    def do_move_cursor_next_scene(self):
        """Move cursor to next scene heading."""
        for i in range(self._cursor_par + 1, len(self._paragraphs)):
            if self._paragraphs[i].get_type() == PType.SCENE:
                self._cursor_pos = 0
                self._cursor_par = i
                break
        else:
            for i in range(0, self._cursor_par):
                if self._paragraphs[i].get_type() == PType.SCENE:
                    self._cursor_pos = 0
                    self._cursor_par = i
                    break

    def do_rebuild_autocomplete_db(self):
        """Rebuild name database."""
        self._name_db.clear()
        for paragraph in self._paragraphs:
            if paragraph.get_type() == PType.NAME:
                self._name_db.add(paragraph.get_text()[:-1])

    def do_save(self, path: str):
        """Save screenplay to path."""
        fountain.write(path, self._paragraphs)
        self._path = path

    def do_undo(self):
        """Undo newest action."""
        if self._current_action < len(self._previous_actions):
            for action in self._previous_actions[self._current_action].actions:
                if type(action) is InputAction:
                    self._delete(action.pindex, action.position, len(action.text), False)
                    self._cursor_par = action.pindex
                    self._cursor_pos = action.position
                elif type(action) is DeleteAction:
                    self._input(action.pindex, action.position, action.text, False)
                    self._cursor_par = action.pindex
                    self._cursor_pos = action.position + len(action.text)
                elif type(action) is NewParagraphAction:
                    self._delete_paragraph(action.pindex, False)
                    if self._cursor_par == action.pindex:
                        self._cursor_par -= 1
                        if self._cursor_par < 0:
                            self._cursor_par = 0
                            self._cursor_pos = 0
                        else:
                            self.do_move_cursor_paragraph_end()
                elif type(action) is DeleteParagraphAction:
                    self._new_paragraph(action.pindex, action.ptype, action.text, False)
                    self._cursor_par = action.pindex
                    self._cursor_pos = 0
                elif type(action) is ChangePTypeAction:
                    self._change_paragraph_type(action.pindex, action.prev_type, False)
            self._current_action += 1

    def do_redo(self):
        """Redo recently undone action."""
        if self._current_action > 0:
            self._current_action -= 1
            for action in reversed(self._previous_actions[self._current_action].actions):
                if type(action) is InputAction:
                    self._input(action.pindex, action.position, action.text, False)
                    self._cursor_par = action.pindex
                    self._cursor_pos = action.position + len(action.text)
                elif type(action) is DeleteAction:
                    self._delete(action.pindex, action.position, len(action.text),
                                 False)
                    self._cursor_par = action.pindex
                    self._cursor_pos = action.position
                elif type(action) is NewParagraphAction:
                    self._new_paragraph(action.pindex, action.ptype, action.text,
                                        False)
                    self._cursor_par = action.pindex
                    self._cursor_pos = 0
                elif type(action) is DeleteParagraphAction:
                    self._delete_paragraph(action.pindex, False)
                    if self._cursor_par == action.pindex:
                        self._cursor_par -= 1
                        if self._cursor_par < 0:
                            self._cursor_par = 0
                            self._cursor_pos = 0
                        else:
                            self.do_move_cursor_paragraph_end()
                elif type(action) is ChangePTypeAction:
                    self._change_paragraph_type(action.pindex, action.new_type, False)

    def get_pindex_at_line(self, line: int) -> (int, int):
        """Return paragraph's index for line and offset into said paragraph."""
        for index in range(len(self._paragraphs)):
            length = self._paragraphs[index].get_line_count()
            if line < length:
                return index, line
            line -= length
        raise ValueError("Not enough lines in screenplay!")

    def get_paragraph_at_index(self, index: int) -> Paragraph:
        """Return paragraph at index."""
        return self._paragraphs[index]

    def get_paragraph_count(self) -> int:
        """Return number of paragraphs."""
        return len(self._paragraphs)

    def get_cursor_info(self) -> (int, int):
        """Return cursor's paragraph index and position in paragraph."""
        line, col = self._paragraphs[self._cursor_par]\
            .get_line_column_at_pos(self._cursor_pos)
        for i in range(0, self._cursor_par):
            line += self._paragraphs[i].get_line_count()
        return line, col

    def get_cursor_paragraph(self) -> Paragraph:
        """Return cursor's paragraph."""
        return self._paragraphs[self._cursor_par]

    def get_path(self) -> str:
        """Get path for screenplay."""
        return self._path

    def get_line_count(self) -> int:
        """Get number of lines."""
        # TODO Optimize (e.g. calculate line count once for every change)
        # Some hints:
        # - Paragraph conversion: Subtract par line count, convert, add new
        # - Input into same paragraph (no \n): Same as paragraph conversion
        count = 0
        for paragraph in self._paragraphs:
            count += paragraph.get_line_count()
        return count

    def __str__(self) -> str:
        """Return screenplay as string."""
        result = ""
        for paragraph in self._paragraphs:
            result += str(paragraph)
        return result
