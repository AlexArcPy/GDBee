# -*- coding: UTF-8 -*-
"""Container of tabs."""

from PyQt5.QtWidgets import (QTabWidget, QAction, QToolButton, QMessageBox)
from PyQt5.QtCore import Qt

from tab import Tab
from geodatabase import Geodatabase
from cfg import dev_mode, not_connected_to_gdb_message


########################################################################
class TabWidget(QTabWidget):
    """Container of tabs."""

    # ----------------------------------------------------------------------
    def __init__(self, parent=None):
        """Initialize TabWidget with basic properties."""
        super(TabWidget, self).__init__(parent)

        self.latest_query_index = 0  # to show as `Query <index>` in tab name

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.on_close_tab_mouse)

        self.close_query_window = QAction('Close tab', self)
        self.close_query_window.setShortcut('Ctrl+W')
        self.close_query_window.triggered.connect(self.on_close_tab_keyboard)
        self.addAction(self.close_query_window)

        self.tab_button = QToolButton(self)
        self.tab_button.setText('+')
        self.tab_button.setToolTip('Add a new tab')
        self.setCornerWidget(self.tab_button, Qt.TopRightCorner)
        self.tab_button.clicked.connect(self.add_tab_page)

        if dev_mode:
            self.add_tab_page()

    # ----------------------------------------------------------------------
    def add_tab_page(self):
        """Add a new empty tab.

        Create empty query panel and empty result table.
        """
        empty_tab = Tab()
        self.latest_query_index += 1
        self.addTab(empty_tab, 'Query {idx}'.format(
            idx=self.latest_query_index))
        if self.tabBar().count() > 1:
            current_tab_gdb = getattr(self.widget(
                self.currentIndex()), 'gdb', None)
            if current_tab_gdb:
                empty_tab.gdb = current_tab_gdb
                empty_tab.connected_gdb_path_label.setText(
                    self.widget(self.currentIndex()).gdb.path)
                empty_tab.connect_to_geodatabase(
                    evt=None, triggered_with_browse=False)
                empty_tab._fill_toc()
            else:  # the first tab
                empty_tab.connected_gdb_path_label.setText(
                    not_connected_to_gdb_message)

        # focus on the newly added tab
        self.setCurrentWidget(empty_tab)
        # focus on the query text panel to be able to start typing directly
        empty_tab.query.setFocus()

        if dev_mode:
            empty_tab.gdb = Geodatabase('NYC.gdb')
            empty_tab.connected_gdb_path_label.setText(empty_tab.gdb.path)
            empty_tab._set_gdb_items_highlight()
            empty_tab._fill_toc()
            empty_tab.query.setText('select * from streets limit 1000')
            empty_tab.run_query()
        return

    # ----------------------------------------------------------------------
    def on_close_tab_mouse(self, index):
        """Close the tab upon clicking on the close icon confirming first."""
        tab_to_close = self.widget(index)
        if tab_to_close.query.document().toPlainText():
            self.close_tab_handler(index)
        else:
            self.removeTab(index)
        return

    # ----------------------------------------------------------------------
    def close_tab_handler(self, index):
        """Show confirmation message box before closing a tab."""
        msg = QMessageBox()
        msg.setText('Are you sure you want to close this tab?')
        msg.setWindowTitle('Close tab')
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.buttonClicked.connect(
            lambda evt, arg=index: self.close_tab(
                evt, index))
        msg.exec_()
        return

    # ----------------------------------------------------------------------
    def close_tab(self, evt, index):
        """Close tab method."""
        if evt.text() == 'OK':
            self.removeTab(index)
        return

    # ----------------------------------------------------------------------
    def on_close_tab_keyboard(self):
        """Close the tab upon using the keyboard shortcut."""
        index = self.currentIndex()
        tab_to_close = self.widget(index)
        if tab_to_close.query.document().toPlainText():
            self.close_tab_handler(index)
        else:
            self.removeTab(index)
        return
