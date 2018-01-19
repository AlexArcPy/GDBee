# -*- coding: UTF-8 -*-
'''Code completion logic in the text editor'''

import io
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtCore import Qt


########################################################################
class Completer():
    '''Comleter class to use in the query text editor'''

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        with io.open(r'completer_data\keywords.txt', 'r', encoding='utf-8') as f:
            lowercase_keywords = [k.rstrip().lower() for k in f.readlines()]
            uppercase_keywords = [k.upper() for k in lowercase_keywords]
            titlecase_keywords = [k.title() for k in lowercase_keywords]

        with io.open(r'completer_data\functions.txt', 'r', encoding='utf-8') as f:
            titlecase_funcs = [f.rstrip() for f in f.readlines()]
            uppercase_funcs = [f.upper() for f in titlecase_funcs]
            lowercase_funcs = [f.lower() for f in titlecase_funcs]

        self.completer = QCompleter(lowercase_keywords + uppercase_keywords +\
                                    titlecase_keywords + lowercase_funcs +\
                                    uppercase_funcs + titlecase_funcs)

        self.completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setWrapAround(False)
        return
