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

import curses
from enum import Enum

from shane.screenplay import Screenplay, PPrefs, PType
from shane.view import View


class ScreenplayViewEvent(Enum):
    """Enum for results from editing mainloop."""
    ESCAPE = 0
    RESIZE = 1


class ScreenplayView(View):
    """View for screenplay editing."""

    def __init__(self, screenplay: Screenplay):
        """Initialize screenplay view."""
        super().__init__(screenplay)

        self._top_line = 0

    def run(self):
        """Run screenplay view's mainloop."""
        super().run()

        while True:
            self._draw()

            char = self._window.get_wch()
            if type(char) is str:
                asc = ord(char)

                if asc == 8:  # Backspace
                    self._screenplay.do_delete_backward()
                    self._dirty = True
                elif asc == 9:  # Tab
                    self._screenplay.do_convert_tab_style()
                    self._dirty = True
                elif asc == 10:  # Enter
                    if self._screenplay.get_cursor_paragraph().get_type() \
                            == PType.NAME:
                        self._screenplay.do_move_cursor_paragraph_end()
                    self._screenplay.do_input("\n")
                    self._dirty = True
                elif asc == 27:  # ESC
                    self._window.nodelay(True)
                    asc = self._window.getch()
                    self._window.nodelay(False)
                    if asc == -1:
                        return ScreenplayViewEvent.ESCAPE
                elif asc == 95:  # Underscore
                    if self._screenplay.get_cursor_paragraph().get_type() \
                            == PType.NAME:
                        self._screenplay.do_autocomplete_name()
                    else:
                        self._screenplay.do_input("_")
                    self._dirty = True
                elif asc == 127:  # Delete
                    self._screenplay.do_delete_forward()
                    self._dirty = True
                elif 32 <= asc:  # Letter (except underscore)
                    self._screenplay.do_input(char)
                    self._dirty = True
            elif char == curses.KEY_BACKSPACE:
                self._screenplay.do_delete_backward()
                self._dirty = True
            elif char == curses.KEY_DC:
                self._screenplay.do_delete_forward()
                self._dirty = True
            elif char == curses.KEY_SLEFT:  # Shift + left
                self._screenplay.do_convert_to_prev_ptype()
                self._dirty = True
            elif char == curses.KEY_SRIGHT:  # Shift + right
                self._screenplay.do_convert_to_next_ptype()
                self._dirty = True
            elif char == curses.KEY_LEFT:
                self._screenplay.do_move_cursor_left()
            elif char == curses.KEY_RIGHT:
                self._screenplay.do_move_cursor_right()
            elif char == curses.KEY_UP:
                self._screenplay.do_move_cursor_up()
            elif char == curses.KEY_DOWN:
                self._screenplay.do_move_cursor_down()
            elif char == curses.KEY_HOME:
                self._screenplay.do_move_cursor_line_start()
            elif char == curses.KEY_END:
                self._screenplay.do_move_cursor_line_end()
            elif char == curses.KEY_PPAGE:
                self._screenplay.do_move_cursor_prev_scene()
                self._top_line = self._screenplay.get_cursor_info()[0]
                self._dirty = True
            elif char == curses.KEY_NPAGE:
                self._screenplay.do_move_cursor_next_scene()
                self._top_line = self._screenplay.get_cursor_info()[0]
                self._dirty = True
            elif char == curses.KEY_RESIZE:
                return ScreenplayViewEvent.RESIZE

    def _draw(self):
        """Draw screenplay."""
        cursor_line, cursor_column = self._screenplay.get_cursor_info()

        scrollbar_slider = int(cursor_line / self._screenplay.get_line_count() *
                               (self._height - 1))
        if scrollbar_slider >= self._height - 1:
            scrollbar_slider = self._height - 2

        cursor_line -= self._top_line
        if cursor_line >= self._height:
            self._top_line += cursor_line - self._height + 1
            cursor_line = self._height - 1
            self._dirty = True
        elif cursor_line < 0:
            self._top_line += cursor_line
            cursor_line = 0
            self._dirty = True

        if self._dirty:
            par_index, line_off = \
                self._screenplay.get_pindex_at_line(self._top_line)

            self._window.clear()

            current_line = 0
            while current_line < self._height\
                    and par_index < self._screenplay.get_paragraph_count():
                paragraph = self._screenplay.get_paragraph_at_index(par_index)
                lines = paragraph.get_lines()
                ptype = paragraph.get_type()
                indent = PPrefs.get_indent(ptype)
                width = PPrefs.get_width(ptype)

                for i in range(line_off, len(lines)):
                    if current_line < self._height:
                        if ptype == PType.SCENE:
                            self._window.addnstr(current_line, indent,
                                                 lines[i].upper(), width,
                                                 curses.A_BOLD)
                        elif ptype == PType.PARENTHETICALS:
                            if i == 0:
                                self._window.addstr(current_line, indent - 1,
                                                    "(")
                            if i == len(lines) - 1:
                                self._window.addstr(current_line,
                                                    indent + len(lines[i]) - 1,
                                                    ")")
                            self._window.addnstr(current_line, indent, lines[i],
                                                 width)
                        else:
                            self._window.addnstr(current_line, indent, lines[i],
                                                 width)
                    else:
                        break
                    current_line += 1

                line_off = 0
                par_index += 1

        for y in range(0, self._height - 1):
            self._window.addstr(y, self._width - 1, "|")
        self._window.addstr(scrollbar_slider, self._width - 1, "O")

        cursor_paragraph = self._screenplay.get_cursor_paragraph()
        cursor_ptype = cursor_paragraph.get_type()
        cursor_indent = PPrefs.get_indent(cursor_ptype)
        self._window.move(cursor_line, min(cursor_indent + cursor_column,
                                           cursor_indent +
                                           PPrefs.get_width(cursor_ptype)))

        self._window.refresh()

        self._dirty = False

    def redraw(self):
        """Completely redraw screen view."""
        self._dirty = True
        if self._window:
            self._draw()

    @staticmethod
    def get_required_window_width():
        """Return minimum width needed for view."""
        screenplay_width = 0
        for ptype in PType:
            width = PPrefs.get_indent(ptype) + PPrefs.get_width(ptype)
            if screenplay_width < width:
                screenplay_width = width
        return screenplay_width + 2
