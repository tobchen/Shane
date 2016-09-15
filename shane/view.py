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

from shane.screenplay import Screenplay


class View(object):
    """A screenplay view to display and take input relevant for a screenplay."""

    def __init__(self, screenplay: Screenplay):
        """Initialize view for screenplay."""
        self._screenplay = screenplay
        self._window = None
        self._width = 0
        self._height = 0
        self._dirty = False

    def run(self):
        """Run view (most likely run a main loop)."""
        self._dirty = True

    def _draw(self):
        """Draw view contents."""
        raise NotImplementedError("_draw() not implemented!")

    def set_window(self, window):
        """Set ncurses window to draw on."""
        self._window = window
        self._window.keypad(True)
        self._height, self._width = self._window.getmaxyx()
        self._dirty = True
        self._draw()

    def remove_window(self):
        """Remove ncurses window."""
        self._window = None
