# -*- coding: UTF-8 -*-
"""Tab in the tabbed window."""

import re
import time
import itertools

from highlighter import Highlighter
from text_editor import TextEditor
from completer import Completer
from table import ResultTable
from cfg import not_connected_to_gdb_message, sql_dialects_names
from geodatabase import Geodatabase

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QAction, QPlainTextEdit,
                             QSplitter, QApplication, QStyleFactory, QLabel,
                             QPushButton, QToolBar, QFileDialog, QMessageBox,
                             QTreeWidget, QTreeWidgetItem, QComboBox)
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QKeySequence, QFont


########################################################################
class Tab(QWidget):
    """Tab in the QTableWidget where user executes query and sees the result."""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Initialize Tab with layout and behavior."""
        super(Tab, self).__init__()

        # regex pattern for SQL query block comments
        self.block_comment_re = re.compile(
            r'(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
            re.DOTALL | re.MULTILINE)

        main_layout = QVBoxLayout(self)

        # define gdb props
        self.gdb = None
        self.gdb_items = None
        self.gdb_columns_names = None
        self.gdb_schemas = None

        # connected geodatabase path toolbar
        self.connected_gdb_path_label = QLabel('')
        self.connected_gdb_path_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse)
        self.connected_gdb_path_label.setToolTip(
            'Connected geodatabase that queries will be run against')
        self.connected_gdb_path_label.setText(not_connected_to_gdb_message)

        self.browse_to_gdb = QPushButton('Browse')
        self.browse_to_gdb.setShortcut(QKeySequence('Ctrl+B'))
        self.browse_to_gdb.clicked.connect(
            lambda evt, arg=True: self.connect_to_geodatabase(
                evt, triggered_with_browse=True))

        self.gdb_sql_dialect_combobox = QComboBox()
        for dialect in sql_dialects_names:
            self.gdb_sql_dialect_combobox.addItem(dialect)

        self.gdb_browse_toolbar = QToolBar()
        self.gdb_browse_toolbar.setMaximumHeight(50)
        self.gdb_browse_toolbar.addWidget(self.browse_to_gdb)
        self.gdb_browse_toolbar.addWidget(self.connected_gdb_path_label)
        self.gdb_browse_toolbar.addSeparator()
        self.gdb_browse_toolbar.addWidget(self.gdb_sql_dialect_combobox)

        # table with results
        self.table = ResultTable()

        # execute SQL query
        self.execute = QAction('Execute', self)
        self.execute.setShortcuts(
            [QKeySequence('F5'),
             QKeySequence('Ctrl+Return')])
        self.execute.triggered.connect(self.run_query)
        self.addAction(self.execute)

        # enter a SQL query
        self.query = TextEditor()
        self.query.setPlainText('')
        font = self.query.font()
        font.setFamily('Consolas')
        font.setStyleHint(QFont.Monospace)

        # TODO: add line numbers to the text editor
        font.setPointSize(14)
        self.query.setFont(font)
        self.query.setTabStopWidth(20)
        self.highlighter = Highlighter(self.query.document())

        # TODO select block of text - Ctrl+/ and they become comments
        self.completer = Completer()
        self.query.set_completer(self.completer.completer)

        # errors panel to show if query fails to execute properly
        self.errors_panel = QPlainTextEdit()
        font = self.query.font()
        font.setPointSize(12)
        self.errors_panel.setStyleSheet('color:red')
        self.errors_panel.setFont(font)
        self.errors_panel.hide()

        # splitter between the toolbar, query window, and the result set table
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.gdb_browse_toolbar)
        splitter.addWidget(self.query)
        splitter.addWidget(self.table)
        splitter.addWidget(self.errors_panel)

        # add the settings after the widget have been added
        splitter.setCollapsible(0, True)
        splitter.setCollapsible(1, False)
        splitter.setCollapsible(2, False)
        splitter.setCollapsible(3, False)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 7)
        splitter.setSizes((100, 200, 300))
        self.table.hide()

        # TOC
        self.toc = QTreeWidget()
        self.toc.setHeaderHidden(True)

        # second splitter between the TOC to the left and the query/table to the
        # right
        toc_splitter = QSplitter(Qt.Horizontal)
        toc_splitter.addWidget(self.toc)
        toc_splitter.addWidget(splitter)
        toc_splitter.setCollapsible(0, True)
        toc_splitter.setSizes((200, 800))  # set the TOC vs data panel

        main_layout.addWidget(toc_splitter)

        margins = QMargins()
        margins.setBottom(10)
        margins.setLeft(10)
        margins.setRight(10)
        margins.setTop(10)
        main_layout.setContentsMargins(margins)

        self.setLayout(main_layout)
        QApplication.setStyle(QStyleFactory.create('Cleanlooks'))
        self.show()

        return

    # ----------------------------------------------------------------------
    def connect_to_geodatabase(self, evt, triggered_with_browse=True):
        """Connect to geodatabase by letting user browse to a gdb folder."""
        if triggered_with_browse:
            gdb_connect_dialog = QFileDialog(self)
            gdb_connect_dialog.setFileMode(QFileDialog.Directory)
            gdb_path = gdb_connect_dialog.getExistingDirectory()

            # TODO: add a filter to show only .gdb folders?
            # https://stackoverflow.com/questions/4893122/filtering-in-qfiledialog
            if gdb_path and gdb_path.endswith('.gdb'):
                self.gdb = Geodatabase(gdb_path)
                if self.gdb.is_valid():
                    self.connected_gdb_path_label.setText(self.gdb.path)
                    self._set_gdb_items_highlight()
                    self._set_gdb_items_complete()
                    self._fill_toc()
                else:
                    msg = QMessageBox()
                    msg.setText('This is not a valid file geodatabase')
                    msg.setWindowTitle('Validation error')
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
        else:
            if self.gdb.is_valid():
                self._set_gdb_items_highlight()
                self._set_gdb_items_complete()

        return

    # ----------------------------------------------------------------------
    def wheelEvent(self, event):  # noqa: N802
        """Override built-in method to handle mouse wheel scrolling.

        Necessary to do when the tab is focused.
        """
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            if event.angleDelta().y() > 0:  # scroll forward
                self.query.zoomIn(1)
            else:
                self.query.zoomOut(1)
        return

    # ----------------------------------------------------------------------
    def run_query(self):
        """Run SQL query and draw the record set and call table drawing."""
        if not self.gdb:
            self.print_sql_execute_errors(not_connected_to_gdb_message)
            return
        try:
            if not self.gdb.is_valid():
                return

            # use the text of what user selected, if none -> need to run the
            # whole query
            part_sql_query = self.query.textCursor().selection().toPlainText()

            if part_sql_query:
                sql_query = part_sql_query
            else:
                sql_query = self.query.toPlainText()

            if sql_query:
                # removing block comments and single line comments
                sql_query = self.block_comment_re.sub(
                    self._strip_block_comments, sql_query)
                sql_query = self._strip_single_comments(sql_query)
            else:
                return

            # TODO: add threading to allow user to cancel a long running query
            QApplication.setOverrideCursor(Qt.WaitCursor)
            start_time = time.time()
            self.gdb.open_connection()
            res, errors = self.gdb.execute_sql(
                sql_query, self.gdb_sql_dialect_combobox.currentText())
            end_time = time.time()
            if errors:
                self.print_sql_execute_errors(errors)

            if res:
                self.table.show()
                self.errors_panel.hide()
                self.draw_result_table(res)
                msg = 'Executed in {exec_time:.1f} secs | {rows} rows'.format(
                    exec_time=end_time - start_time,
                    rows=self.table.table_data.number_layer_rows)
                self.update_app_status_bar(msg)

        except Exception as err:
            print(err)
        finally:
            QApplication.restoreOverrideCursor()
        return

    # ----------------------------------------------------------------------
    def result_should_include_geometry(self):
        """Get the setting defining whether to include the geometry column."""
        try:
            return self.parentWidget().parentWidget().parentWidget(
            ).do_include_geometry.isChecked()
        except BaseException:
            return True

    # ----------------------------------------------------------------------
    def update_app_status_bar(self, message):
        """Update app status bar with the execution result details."""
        try:
            self.parentWidget().parentWidget().parentWidget().statusBar(
            ).showMessage(message)
        except BaseException:
            pass
        return

    # ----------------------------------------------------------------------
    def draw_result_table(self, res):
        """Draw table with the record set received from the geodatabase."""
        geom_col_name = res.GetGeometryColumn(
        )  # shape col was in the sql query
        self.geometry_isin_query = bool(geom_col_name)

        self.table.draw_result(
            res, show_shapes=bool(self.result_should_include_geometry()))
        self.table.view.resizeColumnsToContents()
        return

    # ----------------------------------------------------------------------
    def print_sql_execute_errors(self, err):
        """Print to a special panel errors that occurred during execution."""
        self.table.hide()
        self.errors_panel.show()
        self.errors_panel.setPlainText(err)
        return

    # ----------------------------------------------------------------------
    def _set_gdb_items_highlight(self):
        """Set completer and highlight properties for geodatabase items."""
        self.gdb_items = self.gdb.get_items()
        self.highlighter.set_highlight_rules_gdb_items(self.gdb_items, 'Table')

        self.gdb_schemas = self.gdb.get_schemas()
        self.gdb_columns_names = sorted(
            list(
                set(
                    itertools.chain.from_iterable(
                        [i.keys() for i in self.gdb_schemas.values()]))),
            key=lambda x: x.lower())

    # ----------------------------------------------------------------------
    def _set_gdb_items_complete(self):
        """Update completer rules to include geodatabase items."""
        self.completer.update_completer_string_list(self.gdb_items +
                                                    self.gdb_columns_names)
        self.highlighter.set_highlight_rules_gdb_items(self.gdb_columns_names,
                                                       'Column')
        return

    # ----------------------------------------------------------------------
    def _fill_toc(self):
        """Fill TOC with geodatabase datasets and columns."""
        self.toc.clear()
        if not self.gdb_items:
            return

        for tbl_name in sorted(self.gdb_items, key=lambda i: i.lower()):
            if tbl_name.islower() or tbl_name.isupper():
                item = QTreeWidgetItem([tbl_name.title()])
            else:
                item = QTreeWidgetItem([tbl_name])
            font = QFont()
            font.setBold(True)
            item.setFont(0, font)

            for col_name, col_type in sorted(
                    self.gdb_schemas[tbl_name].items()):
                if col_name.islower() or col_name.isupper():
                    col_name = col_name.title()

                item_child = QTreeWidgetItem(
                    ['{0} ({1})'.format(col_name, col_type)])
                item.addChild(item_child)
            self.toc.addTopLevelItem(item)
        return

    # ----------------------------------------------------------------------
    def _do_toc_hide_show(self):
        """Hide TOC with tables and columns."""
        if self.toc.isVisible():
            self.toc.setVisible(False)
        else:
            self.toc.setVisible(True)
        return

    # ----------------------------------------------------------------------
    def _strip_block_comments(self, sql_query):
        """Strip the block comments in SQL query."""
        start, mid, end = sql_query.group(1, 2, 3)
        if mid is None:
            # this is a single-line comment
            return ''
        elif start is not None or end is not None:
            # this is a multi-line comment at start/end of a line
            return ''
        elif '\n' in mid:
            # this is a multi-line comment with line break
            return '\n'
        else:
            # this is a multi-line comment without line break
            return ' '

    # ----------------------------------------------------------------------
    def _strip_single_comments(self, sql_query):
        """Strip the single line comments in SQL query."""
        clean_query = []
        for line in sql_query.rstrip().split('\n'):
            clean_line = line.split('--')[0]
            if clean_line:
                clean_query.append(clean_line)
        return ' '.join([line for line in clean_query])
