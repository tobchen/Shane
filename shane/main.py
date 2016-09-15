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
import os
import sys
from enum import Enum
import locale

from shane.screenplay import Screenplay
from shane.sp_view import ScreenplayView, ScreenplayViewEvent

from shane.menu_view import MenuView, MenuViewEvent


class ActiveWindow(Enum):
    """Enum for recording the currently active view."""

    SCREENPLAY = 0
    MENU = 1
    NONE = 2


def main(stdscr):
    """Run *Shane.*"""
    path = sys.argv[1] if len(sys.argv) > 1 else None
    screenplay = Screenplay(path)

    size = stdscr.getmaxyx()

    sp_view_width = ScreenplayView.get_required_window_width()
    if size[1] < sp_view_width or size[0] < 2:
        raise RuntimeError("Terminal's not large enough! Must be at least " +
                           str(sp_view_width) + " x 2!")

    screenplay_window = curses.newwin(size[0] - 1, sp_view_width, 1,
                                      int((size[1] - sp_view_width) / 2))
    screenplay_view = ScreenplayView(screenplay)
    screenplay_view.set_window(screenplay_window)

    menu_window = curses.newwin(1, size[1], 0, 0)
    menu_view = MenuView(screenplay)
    menu_view.set_window(menu_window)

    active_window = actual_active_window = ActiveWindow.SCREENPLAY

    while True:
        resize = False

        if active_window == ActiveWindow.SCREENPLAY:
            event = screenplay_view.run()
            if event == ScreenplayViewEvent.ESCAPE:
                active_window = actual_active_window = ActiveWindow.MENU
            elif event == ScreenplayViewEvent.RESIZE:
                resize = True
        elif active_window == ActiveWindow.MENU:
            event = menu_view.run()
            if event == MenuViewEvent.ESCAPE:
                active_window = actual_active_window = ActiveWindow.SCREENPLAY
            elif event == MenuViewEvent.QUIT:
                break
            elif event == MenuViewEvent.RESIZE:
                resize = True
            elif event == MenuViewEvent.REDRAW_SCREEN_VIEW:
                screenplay_view.redraw()
        elif active_window == ActiveWindow.NONE:
            char = stdscr.getch()
            if char == 27:
                break
            elif char == curses.KEY_RESIZE:
                resize = True

        if resize:
            size = stdscr.getmaxyx()

            if "screenplay_window" in locals():
                screenplay_view.remove_window()
                del screenplay_window
            if "menu_window" in locals():
                menu_view.remove_window()
                del menu_window

            if size[1] < sp_view_width or size[0] < 2:
                stdscr.clear()
                stdscr.addstr(0, 0, "Terminal to small!")
                stdscr.refresh()

                active_window = ActiveWindow.NONE
            else:
                stdscr.clear()
                stdscr.refresh()

                screenplay_window = curses.newwin(size[0] - 1, sp_view_width, 1,
                                                  int((size[1] -
                                                       sp_view_width) / 2))
                screenplay_view.set_window(screenplay_window)

                menu_window = curses.newwin(1, size[1], 0, 0)
                menu_view.set_window(menu_window)

                active_window = actual_active_window


def run():
    """Run *Shane* by wrapping its main, preventing terminal corruption."""
    locale.setlocale(locale.LC_ALL, "")

    try:
        # A LOT of thanks to this guy for the delay thing:
        # http://en.chys.info/2009/09/esdelay-ncurses/
        if "ESCDELAY" not in os.environ:
            os.environ["ESCDELAY"] = "25"
        curses.wrapper(main)
    except RuntimeError as error:
        print(error)
    except KeyboardInterrupt:  # Not my fault people chose to quit this way!
        pass
