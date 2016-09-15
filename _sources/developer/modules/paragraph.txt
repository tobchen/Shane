=========
Paragraph
=========

Paragraphs are defined by their types. They contain text and with every edit
they rebuild a list of characters per line used to cut up their text into lines
(for display with word wrap).

Design Decisions
================

The only currently available paragraph types are ``SCENE``, ``ACTION``,
``NAME``, ``PARENTHETICALS``, ``DIALOG``. Transitions are notably missing but
as they are frowned upon won't most likely ever get into *Shane* (there are
probably useful edge cases for transitions but they are few and far between).
*Shane* is supposed to be a simple alternative and will never be bloated up with
screenplay elements that are almost definitely never used or actually needed.

Coding Standard Specifics
=========================

``Paragraph`` methods that make changes to the paragraph (i.e. are not getters)
are to be prefixed with ``sp_`` and called only by the paragraph itself or the
:doc:`screenplay`.

Source Code Docstrings
======================

.. automodule:: shane.paragraph
   :members:
