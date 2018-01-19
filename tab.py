# -*- coding: UTF-8 -*-
'''Tab in the tabbed window'''

import re
import ogr
import pandas as pd

from highlighter import Highlighter
from text_editor import TextEditor
from completer import Completer
from table import ResultTable
from cfg import dev_mode, not_connected_to_gdb_message

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QTableWidget, QAction, QPlainTextEdit,
                             QSplitter, QApplication, QStyleFactory, QTableWidgetItem,
                             QLabel, QPushButton, QToolBar, QFileDialog)
from PyQt5.QtCore import Qt, QMargins, QEvent
from PyQt5.QtGui import QKeySequence, QFont


########################################################################
class Tab(QWidget):
    '''A tab in the QTableWidget where user executes query and sees the result'''

    #----------------------------------------------------------------------
    def __init__(self):
        super(Tab, self).__init__()

        # regex pattern for SQL query block comments
        self.block_comment_re = re.compile(
            r'(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?', re.DOTALL | re.MULTILINE)

        # dialect for SQL queries against file geodatabase
        self.dialect = 'SQLITE'  # default is 'OGRSQL' which is less capable

        ogr.UseExceptions()
        main_layout = QHBoxLayout(self)
        self.gdb = ''

        # connected geodatabase path toolbar
        self.connected_gdb_path_label = QLabel('')
        self.connected_gdb_path_label.setToolTip("Connected geodatabase that queries "
                                                 "will be run against")
        self.connected_gdb_path_label.setText(not_connected_to_gdb_message)

        self.browse_to_gdb = QPushButton('Browse')
        self.browse_to_gdb.clicked.connect(self.connect_to_geodatabase)

        self.gdb_browse_toolbar = QToolBar()
        self.gdb_browse_toolbar.setMaximumHeight(50)
        self.gdb_browse_toolbar.addWidget(self.browse_to_gdb)
        self.gdb_browse_toolbar.addWidget(self.connected_gdb_path_label)

        # table with results
        self.table = ResultTable()
        self.nbrow, self.nbcol = 0, 0
        self.table.setRowCount(self.nbrow)
        self.table.setColumnCount(self.nbcol)

        # execute SQL query
        self.execute = QAction('Execute', self)
        self.execute.setShortcuts([QKeySequence('F5'), QKeySequence('Ctrl+Return')])
        self.execute.triggered.connect(self.execute_sql)
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
        self.completer = Completer().completer
        self.query.set_completer(self.completer)

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

        main_layout.addWidget(splitter)

        margins = QMargins()
        margins.setBottom(10)
        margins.setLeft(10)
        margins.setRight(10)
        margins.setTop(10)
        main_layout.setContentsMargins(margins)

        self.setLayout(main_layout)
        QApplication.setStyle(QStyleFactory.create('Cleanlooks'))
        self.show()

        if dev_mode:
            self.gdb = r'NYC.gdb'
            self.connected_gdb_path_label.setText(self.gdb)
            self.query.setText('select * from streets limit 5')
            self.execute_sql()
        return

    #----------------------------------------------------------------------
    def connect_to_geodatabase(self):
        """connect to geodatabase by letting user browse to a gdb folder"""
        gdb_connect_dialog = QFileDialog(self)
        gdb_connect_dialog.setFileMode(QFileDialog.Directory)
        gdb_path = gdb_connect_dialog.getExistingDirectory()

        # TODO: add a filter to show only .gdb folders?
        # https://stackoverflow.com/questions/4893122/filtering-in-qfiledialog
        if gdb_path and gdb_path.endswith('.gdb'):
            self.gdb = gdb_path
            self.connected_gdb_path_label.setText(self.gdb)
        return

    #----------------------------------------------------------------------
    def wheelEvent(self, event):
        """overriding built-in method to handle mouse wheel scrolling when
        the tab is focused"""
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            if event.angleDelta().y() > 0:  # scroll forward
                self.query.zoomIn(1)
            else:
                self.query.zoomOut(1)
        return

    #----------------------------------------------------------------------
    def execute_sql(self):
        """execute SQL query and draw the record set and call table drawing"""
        # http://gdal.org/python/osgeo.ogr.DataSource-class.html#ExecuteSQL
        if not self.gdb:
            self.print_sql_execute_errors(not_connected_to_gdb_message)
            return
        try:
            ds = ogr.Open(self.gdb, 0)  # read-only mode

            # use the text of what user selected, if none -> need to run the whole query
            part_sql_query = self.query.textCursor().selection().toPlainText()

            sql_query = part_sql_query if part_sql_query else self.query.toPlainText()
            if sql_query:
                # removing block comments and single line comments
                sql_query = self.block_comment_re.sub(self._strip_block_comments,
                                                      sql_query)
                sql_query = self._strip_single_comments(sql_query)
            else:
                return

            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                res = None
                if self.dialect == 'SQLITE':
                    do_commit_transaction = False
                res = ds.ExecuteSQL(sql_query, dialect=self.dialect)
                if do_commit_transaction:
                    res.CommitTransaction()
            except Exception as err:
                self.print_sql_execute_errors(err.args[0])

            if res:
                self.table.show()
                self.errors_panel.hide()
                self.nbrow = res.GetFeatureCount()
                self.draw_result_table(res)

        except Exception as err:
            print(err)
        finally:
            QApplication.restoreOverrideCursor()
            if ds:
                ds.Destroy()
        return

    #----------------------------------------------------------------------
    def result_should_include_geometry(self):
        """get whether the setting to include the geometry column was checked"""
        try:
            return self.parentWidget().parentWidget().parentWidget(
            ).do_include_geometry.isChecked()
        except:
            return True

    #----------------------------------------------------------------------
    def draw_result_table(self, res):
        """draw table with the record set received from the database"""
        self.table.verticalHeader().show()
        self.table.horizontalHeader().show()
        self.table.setShowGrid(True)

        # TODO: how to make shape field appear in the right order?
        # currently always in the end
        geom_col_name = res.GetGeometryColumn()  # shape col was in the sql query

        columns_names = [field.name for field in res.schema]
        self.table.columns_names = columns_names
        if geom_col_name and self.result_should_include_geometry():
            columns_names.append(geom_col_name)
        self.nbcol = len(columns_names)

        self.table.setRowCount(self.nbrow)
        self.table.setColumnCount(self.nbcol)
        self.table.setHorizontalHeaderLabels(columns_names)

        row_num = 0
        for i in range(0, self.nbrow):
            feat = res.GetNextFeature()
            if feat:
                attrs_dict = feat.items()
                col_num = 0
                for col_name in columns_names:
                    if col_name == geom_col_name:
                        wkt = feat.geometry().ExportToWkt()
                        if len(wkt) > 60:
                            cell_value = wkt[:60] + '...'
                        else:
                            cell_value = wkt
                    else:
                        cell_value = attrs_dict[col_name]

                    cell = QTableWidgetItem(str(cell_value))
                    if col_name == geom_col_name:
                        cell._wkt = wkt
                    cell.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.table.setItem(row_num, col_num, cell)

                    col_num += 1
                row_num += 1

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        return

    #----------------------------------------------------------------------
    def print_sql_execute_errors(self, err):
        """print the errors that occurred in a special panel"""
        self.table.hide()
        self.errors_panel.show()
        self.errors_panel.setPlainText(err)
        return

    #----------------------------------------------------------------------
    def _strip_block_comments(self, sql_query):
        """strip the block comments in SQL query"""
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

    #----------------------------------------------------------------------
    def _strip_single_comments(self, sql_query):
        """strip the single line comments in SQL query"""
        clean_query = []
        for line in sql_query.rstrip().split('\n'):
            clean_line = line.split('--')[0]
            if clean_line:
                clean_query.append(clean_line)
        return ' '.join([line for line in clean_query])
