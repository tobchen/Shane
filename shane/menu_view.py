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

from shane.screenplay import Screenplay
from shane.view import View


class MenuViewEvent(Enum):
    """Enum for results from menu mainloop."""

    ESCAPE = 0
    RESIZE = 1
    QUIT = 3
    REDRAW_SCREEN_VIEW = 4


class Menu(Enum):
    """Enum for current menu state."""

    TOP = 0
    SAVE_AS = 1
    QUIT = 2
    REBUILD_NAME_DB = 3
    UNDO = 4
    REDO = 5
    SAVE_ERROR = 6


class MenuView(View):
    """View for screenplay menu."""

    buttons = [(Menu.SAVE_AS, "Save As"), (Menu.UNDO, "Undo"),
               (Menu.REDO, "Redo"), (Menu.REBUILD_NAME_DB, "Rebuild Name DB"),
               (Menu.QUIT, "Quit")]

    def __init__(self, screenplay: Screenplay):
        """Initialize menu view."""
        super().__init__(screenplay)

        self._current_button = 0
        self._current_menu = Menu.TOP

        self._save_path = ""

    def run(self):
        """Run menu view's mainloop."""
        super().run()

        while True:
            self._draw()

            char = self._window.getch()

            escape = False
            if char == 27:  # ESC
                self._window.nodelay(True)
                char = self._window.getch()
                self._window.nodelay(False)
                if char == -1:
                    escape = True
            elif char == curses.KEY_RESIZE:
                return MenuViewEvent.RESIZE

            if self._current_menu == Menu.TOP:
                if char == curses.KEY_LEFT:
                    self._current_button -= 1
                    if self._current_button < 0:
                        self._current_button = len(MenuView.buttons) - 1
                elif char == curses.KEY_RIGHT:
                    self._current_button += 1
                    if self._current_button >= len(MenuView.buttons):
                        self._current_button = 0
                elif char == 10:
                    if MenuView.buttons[self._current_button][0]\
                            == Menu.SAVE_AS:
                        self._save_path = self._screenplay.get_path()
                        if not self._save_path:
                            self._save_path = ""
                        self._current_menu = Menu.SAVE_AS
                    elif MenuView.buttons[self._current_button][0] ==\
                            Menu.UNDO:
                        self._screenplay.do_undo()
                        return MenuViewEvent.REDRAW_SCREEN_VIEW
                    elif MenuView.buttons[self._current_button][0] == \
                            Menu.REDO:
                        self._screenplay.do_redo()
                        return MenuViewEvent.REDRAW_SCREEN_VIEW
                    elif MenuView.buttons[self._current_button][0] ==\
                            Menu.REBUILD_NAME_DB:
                        self._draw_processing()
                        self._screenplay.do_rebuild_autocomplete_db()
                    elif MenuView.buttons[self._current_button][0] == Menu.QUIT:
                        return MenuViewEvent.QUIT
                elif escape:
                    return MenuViewEvent.ESCAPE

            elif self._current_menu == Menu.SAVE_AS:
                if 32 <= char <= 126:
                    self._save_path += chr(char)
                elif char == 8 or char == curses.KEY_BACKSPACE:
                    if len(self._save_path) > 0:
                        self._save_path = self._save_path[:-1]
                elif char == 10:
                    self._draw_processing()
                    try:
                        self._screenplay.do_save(self._save_path)
                        self._current_menu = Menu.TOP
                    except OSError:
                        self._current_menu = Menu.SAVE_ERROR
                elif escape:
                    self._current_menu = Menu.TOP

            elif self._current_menu == Menu.SAVE_ERROR:
                if char == 10 or escape:
                    self._current_menu = Menu.SAVE_AS

    def _draw(self):
        """Draw menu."""
        self._window.clear()

        if self._current_menu == Menu.TOP:
            menu = ""
            pos = 0
            for i in range(len(MenuView.buttons)):
                menu += "[" + MenuView.buttons[i][1] + "] "
                if i < self._current_button:
                    pos += len(MenuView.buttons[i][1]) + 3
            self._window.addstr(0, 0, menu)
            self._window.move(0, pos)
        elif self._current_menu == Menu.SAVE_AS:
            if self._save_path:
                self._window.addstr(0, 0, self._save_path[-self._width + 1:])
        elif self._current_menu == Menu.SAVE_ERROR:
            self._window.addstr(0, 0, "Error saving!")

        self._window.refresh()

    def _draw_processing(self):
        """Draw processing notice."""
        self._window.refresh()
        self._window.addstr(0, 0, "Processing...")
        self._window.clear()
