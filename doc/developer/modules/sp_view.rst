===============
Screenplay View
===============

The screenplay view takes input and translates it into screenplay commands
(cursor movement, text editing, etc.) and draws the screenplay.

Drawing
=======

Drawing the screenplay is very likely the most time consuming step in *Shane's*
program flow. Here is how it works:

#. Get cursor position (line and column) in screenplay
#. Calculate scrollbar slider position (using screenplay's total line count)
#. If required scroll view either up or down so that cursor's in view
#. Get paragraph the first visible line's in and offset of that line from
   paragraph start
#. Draw all paragraphs visible line by line starting with the first visible line
#. Draw scrollbar
#. Set cursor

Design Decisions
================

The scrollbar is not drawn as far down as it seemingly can be. It can't.
ncurses throws an error when drawing a character at the lower right. A solution
would be to make the screenplay view window one column wider but the aesthetics
wouldn't make up for the "ugliness" in code and more importantly a whole new
column to clear with every draw pass (without actually being drawn on anyway).

Source Code Docstrings
======================

.. automodule:: shane.sp_view
   :members:
