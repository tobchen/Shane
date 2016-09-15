========
Fountain
========

`Fountain <http://fountain.io/>`_ is a plain text markup language for
screenwriting. It doesn't exist for a specific software which makes it perfect
as the current default (and only) input and output format for *Shane*.

Design Decisions
================

Sadly Fountain's syntax seems to be either ambiguously defined or wrongly
interpreted (e.g. `Trelby <http://www.trelby.org/>`_ doesn't precede the scene
heading with an empty line if it's a screenplay's very first element). That's
why it's been decided that the first line of a Fountain file is understood to be
preceded by empty lines.

Also, while Fountain defines a large list of screenplay elements *Shane's*
Fountain reader (and writer) only understand a small subset of them due to not
supporting a large list of screenplay elements itself. Most elements not known
by *Shane* should be read as actions but the user cannot rely on it. *Shane*
understands:

- Scene Headings
- Actions
- Names
- Parentheticals
- Dialogs

Source Code Docstrings
======================

.. automodule:: shane.io.fountain
   :members:
