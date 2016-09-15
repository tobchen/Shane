====
Main
====

This is *Shane's* entry point.

Life Cycle
==========

*Shane* offers two views: A :doc:`sp_view` and a :doc:`menu_view`. (View is a
term used very loosely here.) While they are shown at the same time only one can
have the user's focus.

*Shane* has a "master mainloop" running endlessly. The focused view runs its own
mainloop (each pass taking input and then redrawing) meaning the other view
"stands still." It only leaves its loop to let the master mainloop redraw the
other view (e.g. for every undo the menu view needs the screenplay view to
redraw itself to reflect the change), to let the master mainloop handle a
screen resize or to give up focus.

Source Code Docstrings
======================

.. automodule:: shane.main
   :members:
