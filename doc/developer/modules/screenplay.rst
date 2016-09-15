==========
Screenplay
==========

The screenplay is a list of paragraphs (see :doc:`paragraph`). It remembers the
cursor's position and serves as an interface between :doc:`sp_view` and
paragraphs (meaning a view cannot modify paragraphs directly but has to move
the screenplay's cursor to the appropriate position and call input methods etc.
of the screenplay.)

Editing And the Undo/Redo System
================================

All screenplay methods for editing have to make use of the ``_input``,
``_delete``, ``_new_paragraph``, ``_delete_paragraph`` and
``_change_paragraph_type`` methods *and* make error checks (e.g. don't delete
more text than there is to delete) (error checks planned to happen in those
methods instead of their callers in the future).

Breaking down editing to these five methods ensures a simple undo/redo system.
The undo/redo system makes use of a somewhat stack (not exactly a stack) of
action bundles. An action bundle is a list of actions that happened in a short
period of time.

For example, entering a ``"\n"`` right into a paragraph deletes everything
after the cursor in this paragraph (``_delete``), then creates a new paragraph
with the deleted text (``_new_paragraph``). This pushes an action bundle of two
actions onto the undo stack. If a user types in multiple characters in rapid
succession she creates an action bundle of all those characters.

Undoing an action now means undoing an action bundle by undoing every little
action in the right order. Redoing an action means redoing an action bundle.
This has the nice effect of 1) masking that complex actions are multiple simple
ones and 2) bundling multiple inputs together to potentially be undone later
(no user wants to undo character by character).

.. Name Database
   =============

.. The screenplay's name database sorts each name into one of three lists: One list
   for names starting from A to M, one for names starting from N to Z and one for
   anything else.

Source Code Docstrings
======================

.. automodule:: shane.screenplay
   :members:
