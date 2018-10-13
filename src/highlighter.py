# -*- coding: UTF-8 -*-
"""Rules for highlighting SQL queries against Esri file geodatabase.

Adapted from
https://github.com/baoboa/pyqt5/blob/master/examples/richtext/
syntaxhighlighter.py

#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
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

import io
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import (QTextCharFormat, QColor, QFont, QSyntaxHighlighter)


########################################################################
class Highlighter(QSyntaxHighlighter):
    """Highlighter class to provide text coloring in the query panel."""

    # ----------------------------------------------------------------------
    def __init__(self, parent=None):
        """Initialize Highlighter with basic highlight options."""
        super(Highlighter, self).__init__(parent)

        self.gdb_highlight_settings = {
            'Table': {
                'Foreground': Qt.black,
                'FontWeight': QFont.Bold,
            },
            'Column': {
                'Foreground': Qt.darkGray,
                'FontWeight': QFont.Normal,
            },
        }

        # SQL keywords to show as bold and blue
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(Qt.darkBlue)
        keyword_format.setFontWeight(QFont.Bold)

        with io.open(
                r'completer_data\keywords.txt', 'r', encoding='utf-8') as f:
            self.plain_keywords = [k.rstrip() for k in f.readlines()]

        keyword_patterns = [
            '\\b{0}\\b'.format(plain_keyword)
            for plain_keyword in self.plain_keywords
        ]

        self.highlight_rules = []
        for pattern in keyword_patterns:
            regexp = QRegExp(pattern)
            regexp.setCaseSensitivity(Qt.CaseInsensitive)
            self.highlight_rules.append((regexp, keyword_format))

        numeric_format = QTextCharFormat()
        numeric_format.setForeground(Qt.blue)
        regex = QRegExp(r'\s[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?')
        self.highlight_rules.append((regex, numeric_format))

        # TODO: highlight parens around such as st_x(shape)
        self.set_highlight_rules_comments()
        self.multi_line_comment_format = QTextCharFormat()
        self.multi_line_comment_format.setForeground(Qt.darkGreen)

        self.set_highlight_rules_quotes()

        # function names to show as italic and pink
        function_format = QTextCharFormat()
        function_format.setFontItalic(True)
        function_format.setForeground(QColor(255, 105, 255))
        self.highlight_rules.append((QRegExp('\\b[A-Za-z0-9_]+(?=\\()'),
                                     function_format))

        self.comment_start_expression = QRegExp('/\\*')
        self.comment_end_expression = QRegExp('\\*/')
        return

    # ----------------------------------------------------------------------
    def set_highlight_rules_quotes(self):
        """Strings in quotes (both single and double) to show as red."""
        quote_format = QTextCharFormat()
        quote_format.setForeground(Qt.red)
        self.highlight_rules.append((QRegExp('\".*\"'), quote_format))
        self.highlight_rules.append((QRegExp("'.*\'"), quote_format))
        return

    # ----------------------------------------------------------------------
    def set_highlight_rules_comments(self):
        """Single- and multi-line comments to show as green."""
        single_line_comment_format = QTextCharFormat()
        single_line_comment_format.setForeground(Qt.darkGreen)
        self.highlight_rules.append((QRegExp('--[^\n]*'),
                                     single_line_comment_format))
        return

    # ----------------------------------------------------------------------
    def set_highlight_rules_gdb_items(self, items, item_type):
        """Update highlight rules to include geodatabase datasets."""
        for item in items:
            fmt = QTextCharFormat()
            fmt.setForeground(
                self.gdb_highlight_settings[item_type]['Foreground'])
            fmt.setFontWeight(
                self.gdb_highlight_settings[item_type]['FontWeight'])
            regexp = QRegExp('\\b{0}\\b'.format(item))
            regexp.setCaseSensitivity(Qt.CaseInsensitive)
            self.highlight_rules.append((regexp, fmt))

        # need to put the single line comment rules afterwards;
        # otherwise table names are highlighted even when are part of comment
        self.set_highlight_rules_comments()
        self.set_highlight_rules_quotes()
        return

    # ----------------------------------------------------------------------
    def highlightBlock(self, text):  # noqa: N802
        """Reimplementation of the built-in method."""
        for pattern, format_ in self.highlight_rules:
            expression = QRegExp(pattern)
            idx = expression.indexIn(text)
            while idx >= 0:
                length = expression.matchedLength()
                self.setFormat(idx, length, format_)
                idx = expression.indexIn(text, idx + length)

        self.setCurrentBlockState(0)

        start_idx = 0
        if self.previousBlockState() != 1:
            start_idx = self.comment_start_expression.indexIn(text)

        while start_idx >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_idx)

            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_idx
            else:
                matched_length = self.comment_end_expression.matchedLength()
                comment_length = end_index - start_idx + matched_length

            self.setFormat(start_idx, comment_length,
                           self.multi_line_comment_format)
            start_idx = self.comment_start_expression.indexIn(
                text, start_idx + comment_length)
        return
