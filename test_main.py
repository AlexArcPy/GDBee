# -*- coding: UTF-8 -*-
'''Unit tests for the application'''

import unittest

from PyQt5 import QtGui, QtCore
from PyQt5.Qt import Qt
from PyQt5.Qt import QKeySequence, QTextCursor
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest

from window import Window


########################################################################
class TestMainWindow(unittest.TestCase):
    """Test interface of the GDBee application"""

    #----------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """prepare the application configuration and the context"""
        super(TestMainWindow, cls).setUpClass()
        setattr(cls, 'local_gdb', 'NYC.gdb')
        return

    #----------------------------------------------------------------------
    def setUp(self):
        """restart application before each unit test"""
        self.app = QApplication([])
        self.ui = Window()
        self.menu = self.ui.menuBar()
        self.file_menu = self.menu.actions()[0]
        self.result_menu = self.menu.actions()[1]
        self.settings_menu = self.menu.actions()[2]
        self.tab = None
        return

    #----------------------------------------------------------------------
    def tearDown(self):
        pass

    #----------------------------------------------------------------------
    def test_create_new_query_tab(self):
        """create a new tab"""
        self.assertEqual(self._get_tabs_count(), 0)
        self._add_new_query_tab()
        self.assertEqual(self._get_tabs_count(), 1)

        # TODO nothing of this works
        #QTest.keyClicks(self.ui.tab_widget, 'n', Qt.ControlModifier)
        #QTest.keyPress(self.ui, Qt.Key_N, Qt.ControlModifier)
        #QTest.keyClick(self.ui, Qt.Qt.CTRL, Qt.Qt.Key_N) #QKeySequence('Ctrl+N'))
        #Qt.Qt.CTRL, Qt.Qt.Key_N)) #Qt.Qt.Key_F5))
        return

    #----------------------------------------------------------------------
    def test_create_multiple_tabs(self):
        """create several tabs"""
        self.assertEqual(self._get_tabs_count(), 0)
        for i in range(10):
            self.tab = self._add_new_query_tab()
        self.assertEqual(self._get_tabs_count(), 10)
        self.assertEqual(self.ui.tab_widget.tabText(9), 'Query 10')
        return

    #----------------------------------------------------------------------
    def test_close_current_tab(self):
        """close the current tab"""
        self.assertEqual(self._get_tabs_count(), 0)
        self.tab = self._add_new_query_tab()
        self.assertEqual(self._get_tabs_count(), 1)
        self.ui.tab_widget.removeTab(0)
        self.assertEqual(self._get_tabs_count(), 0)
        return

    #----------------------------------------------------------------------
    def test_execute_sql(self):
        """execute SQL query to a connected geodatabase"""
        self.assertEqual(self._get_tabs_count(), 0)
        self.tab = self._add_new_query_tab()
        self.assertEqual(self._get_tabs_count(), 1)
        self._execute_sql('SELECT Name, Type, Oneway FROM streets LIMIT 3')
        self.assertEqual(self.tab.table.rowCount(), 3)
        self.assertEqual(self.tab.table.columnCount(), 3)
        return

    #----------------------------------------------------------------------
    def test_include_shape_in_result(self):
        """include or exclude shape column from the result set"""
        self.assertEqual(self._get_tabs_count(), 0)
        self.tab = self._add_new_query_tab()
        self.assertEqual(self._get_tabs_count(), 1)

        # having the shape column excluded by default
        self.assertTrue(self.ui.do_include_geometry.isChecked())

        self.tab.gdb = self.local_gdb
        self.tab = self.ui.tab_widget.currentWidget()
        self.tab.query.setPlainText(
            'SELECT Name, Type, Oneway, Shape FROM streets LIMIT 3')

        self.tab.execute_sql()
        self.assertEqual(self.tab.table.rowCount(), 3)
        self.assertEqual(self.tab.table.columnCount(), 4)

        # enable getting geometry columns into the output
        self.ui.do_include_geometry.setChecked(False)
        self.assertFalse(self.ui.do_include_geometry.isChecked())

        self.tab.execute_sql()
        self.assertEqual(self.tab.table.rowCount(), 3)
        self.assertEqual(self.tab.table.columnCount(), 3)
        return

    #----------------------------------------------------------------------
    def test_exports(self):
        """export result of SQL query execution in various formats"""
        self.assertEqual(self._get_tabs_count(), 0)
        self.tab = self._add_new_query_tab()
        self.assertEqual(self._get_tabs_count(), 1)

        self.tab.gdb = self.local_gdb
        self.tab = self.ui.tab_widget.currentWidget()
        self.tab.query.setPlainText(
            'SELECT Name, Type, Oneway, Shape FROM streets LIMIT 3')

        self.tab.execute_sql()
        self.assertEqual(self.tab.table.rowCount(), 3)
        self.assertEqual(self.tab.table.columnCount(), 4)

        self.ui.export_result(None, '&Markdown')
        self.assertEqual(
            len(self.ui.export_result_window.result.toPlainText().split('\n')), 5)
        self.ui.export_result_window.close()

        self.ui.export_result(None, '&DataFrame')
        self.assertIn('.csv', self.ui.export_result_window.result.toPlainText())
        self.ui.export_result_window.close()

        self.ui.export_result(None, '&QGIS')
        self.assertEqual(
            len(self.ui.export_result_window.result.toPlainText().split('\n')), 3)
        self.assertIn('MULTILINESTRING',
                      self.ui.export_result_window.result.toPlainText())
        self.ui.export_result_window.close()

        self.ui.export_result(None, '&ArcMap')
        text = self.ui.export_result_window.result.toPlainText()
        self.assertTrue([(w in text) for w in ['arcpy', 'MULTILINESTRING']])

        self.ui.export_result_window.close()
        return

    #----------------------------------------------------------------------
    def test_export_before_execute_sql(self):
        """export result table before any SQL query is executed"""
        self.assertEqual(self._get_tabs_count(), 0)
        self.tab = self._add_new_query_tab()
        self.ui.export_result(None, '&DataFrame')
        return

    #----------------------------------------------------------------------
    def test_export_md_with_no_tabulate_installed(self):
        """export to markdown table with no tabulate package installed"""
        # TODO
        pass

    #----------------------------------------------------------------------
    def test_export_markdown_large_table(self):
        """export table with more than 1K rows; goes into .md file"""
        self.tab = self._add_new_query_tab()
        self._execute_sql('SELECT Name, Type, Oneway, Shape FROM streets LIMIT 1001')
        self.ui.export_result(None, '&Markdown')
        self.assertIn('.md', self.ui.export_result_window.result.toPlainText())
        self.ui.export_result_window.close()
        return

    #----------------------------------------------------------------------
    def test_add_new_tab_after_gdb_is_set(self):
        """add a tab, set its gdb, and then add another tab"""
        self.tab = self._add_new_query_tab()
        self.tab.gdb = self.local_gdb
        self.tab2 = self._add_new_query_tab()
        self.assertEqual(self.tab2.gdb, self.tab.gdb)
        return

    #----------------------------------------------------------------------
    def test_trigger_sql_error(self):
        """execute an invalid SQL query"""
        self.tab = self._add_new_query_tab()
        self._execute_sql('SELECT invalid_column FROM streets LIMIT 3')
        self.assertTrue(self.tab.errors_panel.isVisible())
        self.assertIn('no such column', self.tab.errors_panel.toPlainText())
        self._execute_sql('SELECT * FROM streets LIMIT 3')
        self.assertFalse(self.tab.errors_panel.isVisible())
        return

    #----------------------------------------------------------------------
    def test_connecting_to_invalid_gdb(self):
        """browse to a folder with .gdb extension that is not a valid file gdb"""
        self.tab = self._add_new_query_tab()
        self._execute_sql('SELECT Name FROM streets LIMIT 1',
                          r'C:\Non\Existing\Path\Database.gdb')

        # make sure the application still works
        self.tab = self._add_new_query_tab()
        self._execute_sql('SELECT Name, Type, Oneway FROM streets LIMIT 3')
        self.assertEqual(self.tab.table.rowCount(), 3)
        self.assertEqual(self.tab.table.columnCount(), 3)
        return

    #----------------------------------------------------------------------
    def test_parsing_sql_code_comments(self):
        """test executing multiple SQL queries each containing various comments"""
        self.tab = self._add_new_query_tab()
        sql_query_string = '''
        select name --table
        from streets
        /*
        block comment
        */ limit 3 '''
        self._prepare_query_text(sql_query_string)
        self.tab.execute_sql()
        self.assertTrue(self.tab.table.isVisible())
        self.assertEqual(self.tab.table.rowCount(), 3)
        self.assertEqual(self.tab.table.columnCount(), 1)
        return

    #----------------------------------------------------------------------
    def test_execute_sql_query_selection(self):
        """test executing only selected part of the SQL query"""
        self.tab = self._add_new_query_tab()
        sql_query_string = 'SELECT name FROM streets LIMIT 3\n UPDATE'
        self._prepare_query_text(sql_query_string)
        self.tab.execute_sql()
        self.assertTrue(self.tab.errors_panel.isVisible())
        self.assertIn('UPDATE', self.tab.errors_panel.toPlainText())

        cur = self.tab.query.textCursor()
        cur.setPosition(0)
        cur.setPosition(32, QTextCursor.KeepAnchor)
        self.tab.query.setTextCursor(cur)
        self.assertEqual(self.tab.query.textCursor().selectedText(),
                         sql_query_string[:32])

        self.tab.execute_sql()
        self.assertFalse(self.tab.errors_panel.isVisible())
        self.assertTrue(self.tab.table.isVisible())
        self.assertEqual(self.tab.table.rowCount(), 3)
        self.assertEqual(self.tab.table.columnCount(), 1)
        return

    #----------------------------------------------------------------------
    def test_sql_code_styling(self):
        """test highlighting in SQL query"""
        self.tab = self._add_new_query_tab()
        sql_query_string = 'SELECT name FROM streets LIMIT 3'
        self._prepare_query_text(sql_query_string)

        cur = self.tab.query.textCursor()
        cur.setPosition(0)
        cur.setPosition(6, QTextCursor.KeepAnchor)
        self.tab.query.setTextCursor(cur)

        # TODO: bold is never True even though `select` shown as bold
        # perhaps because I use the regex pattern instead of having bold prop
        #self.query.textCursor().charFormat().font().bold()
        return

    #----------------------------------------------------------------------
    def test_copy_cell_value(self):
        """test select and copy a cell value into a clipboard"""
        self.tab = self._add_new_query_tab()
        sql_query_string = 'SELECT name FROM streets LIMIT 3'
        self._prepare_query_text(sql_query_string)
        self._execute_sql(sql_query_string)

        # TODO send the copy to clipboard command
        # QTest.keyPress(self.ui, QKeySequence.Copy)
        return

    #----------------------------------------------------------------------
    def test_copy_shape_value(self):
        """test select and copy a WKT column cell value into a clipboard"""
        # TODO: copied value should be a valid WKT; the cell value should
        # be shortened with `...` in the end
        return

    #----------------------------------------------------------------------
    def _prepare_query_text(self, sql_query):
        """put SQL query string """
        self.tab.gdb = self.local_gdb
        sql_query_string = sql_query
        self.tab.query.setText(sql_query_string)
        return

    #----------------------------------------------------------------------
    def _execute_sql(self, sql, user_gdb=None):
        """execute SQL query in the current tab"""
        self.tab = self.ui.tab_widget.currentWidget()
        if user_gdb:
            self.tab.gdb = user_gdb
        else:
            self.tab.gdb = self.local_gdb
        self.tab.query.setPlainText(sql)
        self.tab.execute_sql()
        return

    #----------------------------------------------------------------------
    def _get_tabs_count(self):
        """get number of tabs in the tabbed widget"""
        return len(self.ui.tab_widget.tabBar())

    #----------------------------------------------------------------------
    def _add_new_query_tab(self):
        """add a new tab with empty query and empty result table"""
        new_query_action = self.file_menu.menu().actions()[0]
        new_query_action.trigger()
        return self.ui.tab_widget.currentWidget()
