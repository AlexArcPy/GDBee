# -*- coding: UTF-8 -*-
"""The main application entry point."""

import sys

from PyQt5.QtWidgets import QApplication
from window import Window

APP = QApplication([])
WINDOW = Window()
WINDOW.show()
sys.exit(APP.exec_())
