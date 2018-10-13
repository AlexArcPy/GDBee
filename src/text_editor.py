# -*- coding: UTF-8 -*-
"""Query text editor widget.

Adapted from
https://github.com/baoboa/pyqt5/blob/master/examples/tools/customcompleter/
customcompleter.py

#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2012 Digia Plc
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import (QTextCursor, QTextFormat, QColor)
from PyQt5.QtWidgets import (QApplication, QCompleter, QTextEdit)


########################################################################
class TextEditor(QTextEdit):
    """Text editor with text completion for writing queries."""

    # ----------------------------------------------------------------------
    def __init__(self, parent=None):
        """Initialize TextEditor with basic properties."""
        super(TextEditor, self).__init__(parent)
        self._completer = None
        self.keys_to_ignore = [
            Qt.Key_Enter,
            Qt.Key_Return,
            Qt.Key_Escape,
            Qt.Key_Tab,
            Qt.Key_Backtab,
        ]
        # excluding `_` as this is often in SQL spatial functions
        self.special_chars = "~!@#$%^&*()+{}|:\"<>?,./;'[]\\-="
        self.completion_after_chars = 3
        return

    # ----------------------------------------------------------------------
    def insertFromMimeData(self, source):  # noqa: N802
        """Override built-in method to convert rich text to plain text."""
        self.insertPlainText(source.text())
        return

    # ----------------------------------------------------------------------
    def wheelEvent(self, event):  # noqa: N802
        """Override built-in method to handle mouse wheel scrolling.

        Required when doing mouse scrolling with the query panel focused.
        """
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            if event.angleDelta().y() > 0:  # scroll forward
                self.zoomIn(1)
            else:
                self.zoomOut(1)
        else:
            step_size = 100
            cur_val = self.verticalScrollBar().value()
            if event.angleDelta().y() > 0:  # scroll forward
                self.verticalScrollBar().setValue(cur_val - step_size)
            else:
                self.verticalScrollBar().setValue(cur_val + step_size)
        return

    # ----------------------------------------------------------------------
    def completer(self):
        """Get internal completer."""
        return self._completer

    # ----------------------------------------------------------------------
    def set_completer(self, completer):
        """Set completer object and its properties."""
        if self._completer is not None:
            self._completer.activated.disconnect()
        else:
            self._completer = completer
            completer.setWidget(self)
            completer.setCompletionMode(QCompleter.PopupCompletion)

            # PyQt bug? Qt.CaseInsensitive will leave some keywords out;
            # need to use Qt.CaseSensitive and have duplicates of words
            completer.setCaseSensitivity(Qt.CaseSensitive)
            completer.activated.connect(self.insert_completion)
        return

    # ----------------------------------------------------------------------
    def insert_completion(self, completion):
        """Insert complete word after user accepted a suggestion."""
        if self._completer.widget() is not self:
            return

        cur = self.textCursor()
        extra_length = len(completion) - len(self._completer.completionPrefix())
        cur.movePosition(QTextCursor.Left)
        cur.movePosition(QTextCursor.EndOfWord)
        cur.insertText(completion[-extra_length:])
        self.setTextCursor(cur)

    # ----------------------------------------------------------------------
    def get_text_under_cursor(self):
        """Get the text currently under cursor."""
        cur = self.textCursor()
        cur.select(QTextCursor.WordUnderCursor)
        return cur.selectedText()

    # ----------------------------------------------------------------------
    def is_parens_char_near(self):
        """Search for the parens chars around the text cursor."""
        cur = self.textCursor()
        try:
            cur.select(QTextCursor.WordUnderCursor)
            print(cur.selectedText())
            if cur.selectedText() == ')':
                return ')'
            if cur.selectedText() == '(':
                return '('
        except BaseException:
            pass

    # ----------------------------------------------------------------------
    def focusInEvent(self, evt):  # noqa: N802
        """Built-in method to handle focusing event."""
        if self._completer is not None:
            self._completer.setWidget(self)
        super(TextEditor, self).focusInEvent(evt)
        return

    # ----------------------------------------------------------------------
    def highlight_line(self):
        """Highlight the whole line the cursor is on."""
        line_highlight = self.ExtraSelection()
        line_highlight.cursor = self.textCursor()
        line_highlight.format.setProperty(QTextFormat.FullWidthSelection, True)
        line_highlight.format.setBackground(QColor('#f3f0f0'))
        self.setExtraSelections([line_highlight])
        return

    # ----------------------------------------------------------------------
    def keyPressEvent(self, evt):  # noqa: N802
        """Override built-in method to handle user pressing keys."""
        if self._completer is not None and self._completer.popup().isVisible():
            if evt.key() in self.keys_to_ignore:
                evt.ignore()
                return

        is_shortcut = ((evt.modifiers() & Qt.ControlModifier) != 0
                       and evt.key() == Qt.Key_F1)
        if self._completer is None or not is_shortcut:
            super(TextEditor, self).keyPressEvent(evt)

        ctrl_shift = evt.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if self._completer is None or (ctrl_shift and len(evt.text()) == 0):
            return

        has_modifier = (evt.modifiers() != Qt.NoModifier) and not ctrl_shift
        cmpl_prefix = self.get_text_under_cursor()

        # if no text entered or text is yet too short -> no completion
        if not is_shortcut and (has_modifier or len(evt.text()) == 0 or
                                len(cmpl_prefix) < self.completion_after_chars
                                or evt.text()[-1] in self.special_chars):
            self._completer.popup().hide()
            return

        # if what user enters already matches the suggestion -> reset
        if cmpl_prefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(cmpl_prefix)
            self._completer.popup().setCurrentIndex(
                self._completer.completionModel().index(0, 0))

        # draw the rectangle with suggestions
        rect = self.cursorRect()
        rect.setWidth(self._completer.popup().sizeHintForColumn(0) + self.
                      _completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(rect)
        return
