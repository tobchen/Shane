===========
User Manual
===========

Requirements
============

:OS: Linux or MacOS
:Software: Python 3.3 or higher, ncurses

Installation
============

*Shane* does *not* need to be installed. Still, if you like to then run
``python setup.py install`` on the command line from *Shane's* root directory.

Run
===

Either run ``python run.py`` from *Shane's* root directory or (if installed)
simply run ``shane`` from wherever. To start *Shane* with opening a screenplay
(for supported file formats, see `Supported File Formats`_) add the path as
a parameter, e.g. ``python run.py /home/hotshot/screenplays/romcom.fountain``
or ``shane /home/hotshot/screenplays/romcom.fountain``.

Usage
=====

This is how to use *Shane:*

Screenplay Window
-----------------

The screenplay window is where the magic happens! Type in or delete characters
and navigate through the script!

Press ``Esc`` to switch to the menu.

Movement
########

Use the arrow keys or ``Home`` or ``End`` to move the cursor.

Press ``Page Up`` or ``Page Down`` to jump to the previous or next scene heading.

New Paragraphs And Conversion
#############################

Press ``Enter`` to create a new paragraph. Which type this new paragraph's of
depends on the current paragraph's type. ``Enter`` works slightly different for
``NAME`` paragraphs in that it won't cut up the paragraph.

Press ``Tab`` to convert the current paragraph. Which type this converts to
depends on the paragraph's current type.

+--------------------+------------+--------------------+
| Paragraph Type     | ``Enter``  | ``Tab``            |
+====================+============+====================+
| ``SCENE``          | ``ACTION`` | ``ACTION``         |
+--------------------+------------+--------------------+
| ``ACTION``         | ``ACTION`` | ``NAME``           |
+--------------------+------------+--------------------+
| ``NAME``           | ``DIALOG`` | ``ACTION``         |
+--------------------+------------+--------------------+
| ``PARENTHETICALS`` | ``DIALOG`` | ``DIALOG``         |
+--------------------+------------+--------------------+
| ``DIALOG``         | ``NAME``   | ``PARENTHETICALS`` |
+--------------------+------------+--------------------+

Use ``Shift`` with the left or right arrow keys to cycle through types for the
current paragraph backward or forward, respectively. The forward order being
``SCENE``, ``ACTION``, ``NAME``, ``PARENTHETICALS``, ``DIALOG``.

Autocomplete
############

Press ``_`` (underscore) in a ``NAME`` paragraph to autocomplete a name (and
cycle through names). For autocomplete to work at least one character must have
already been typed in. Also, a name database must have been built, see
`Rebuild Name DB`_.

Menu
----

Use the arrow keys to navigate through the top level menu. Press ``Esc`` to
switch the screenplay window. Press ``Enter`` to go to the highlighted sub menu
or menu item.

Save As
#######

Type in the path to save the screenplay to, then hit ``Enter`` to save. Press
``Esc`` to cancel and go back to the top level menu. For supported file formats,
see `Supported File Formats`_.

Undo
####

Undo previous action.

Redo
####

Redo previously undone action.

Rebuild Name DB
###############

For autocomplete to work a name database has to be built (and rebuilt for every
new or deleted character) (automatic building planned for future versions).
This menu item will do just that.

Quit
####

Quit *Shane.*

Supported File Formats
======================

*Shane* reads

- Fountain (\*.fountain)

and writes

- Fountain (\*.fountain)

Frequently Asked Questions
==========================

**Why no transitions?** *Shane's* developer doesn't like them. Is that a good
reason to keep everyone else from using them? Probably: The very rare (and still
avoidable) cases transitions *are* useful don't make up for cluttering up
*Shane's* source code.
