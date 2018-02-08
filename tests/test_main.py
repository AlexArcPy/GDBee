# -*- coding: UTF-8 -*-
'''Unit tests for the application'''

import os
import sys
import unittest

from PyQt5.Qt import Qt
from PyQt5.Qt import QTextCursor, QModelIndex, QItemSelectionModel
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest

sys.path.insert(0,
                os.path.join(
                    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                    'src'))
os.chdir(sys.path[0])

from window import Window
from geodatabase import Geodatabase as GDB


########################################################################
class TestMainWindow(unittest.TestCase):
    """Test interface of the GDBee application"""

    #----------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """prepare the application configuration and the context"""
        super(TestMainWindow, cls).setUpClass()
        setattr(cls, 'local_gdb', GDB('NYC.gdb'))
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
        QTest.qWaitForWindowExposed(self.ui)
        return

    #----------------------------------------------------------------------
    def tearDown(self):
        pass

    #----------------------------------------------------------------------
    def test_create_new_query_tab(self):
        """create a new tab triggering the actions and using the keyboard"""
        self.assertEqual(self._get_tabs_count(), 0)
        self._add_new_query_tab()
        self.assertEqual(self._get_tabs_count(), 1)

        QTest.keyPress(self.ui, Qt.Key_N, Qt.ControlModifier)
        self.assertEqual(self._get_tabs_count(), 2)
        return

    #----------------------------------------------------------------------
    def test_create_multiple_tabs(self):
        """create several tabs"""
        self.assertEqual(self._get_tabs_count(), 0)
        for i in range(3):
            self.tab = self._add_new_query_tab()
        self.assertEqual(self._get_tabs_count(), 3)
        self.assertEqual(self.ui.tab_widget.tabText(2), 'Query 3')
        return

    #----------------------------------------------------------------------
    def test_close_current_tab(self):
        """close the current tab triggering the action and using keyboard"""
        self.assertEqual(self._get_tabs_count(), 0)
        self.tab = self._add_new_query_tab()
        self.tab = self._add_new_query_tab()
        self.assertEqual(self._get_tabs_count(), 2)
        self.ui.tab_widget.removeTab(0)
        self.assertEqual(self._get_tabs_count(), 1)

        QTest.keyPress(self.ui, Qt.Key_W, Qt.ControlModifier)
        self.assertEqual(self._get_tabs_count(), 0)

        return

    #----------------------------------------------------------------------
    def test_execute_sql(self):
        """execute SQL query to a connected geodatabase"""
        self.assertEqual(self._get_tabs_count(), 0)
        self.tab = self._add_new_query_tab()
        self.assertEqual(self._get_tabs_count(), 1)
        self._execute_sql('SELECT Name, Type, Oneway FROM streets LIMIT 3')
        self.assertEqual(self.tab.table.table_data.headers, ['NAME', 'TYPE', 'ONEWAY'])
        self.assertEqual(self.tab.table.table_data.number_layer_rows, 3)
        self.assertEqual(self.tab.table.table_data.columnCount(), 3)
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

        self.tab.run_query()
        self.assertEqual(self.tab.table.table_data.number_layer_rows, 3)
        self.assertEqual(self.tab.table.table_data.columnCount(), 4)

        # enable getting geometry columns into the output
        self.ui.do_include_geometry.setChecked(False)
        self.assertFalse(self.ui.do_include_geometry.isChecked())

        self.tab.run_query()
        self.assertEqual(self.tab.table.table_data.number_layer_rows, 3)
        self.assertEqual(self.tab.table.table_data.columnCount(), 3)
        return

    #----------------------------------------------------------------------
    def test_export_qgis(self):
        """export result of SQL query execution to a QGIS QuickWKT plugin format"""
        self._prepare_for_export()
        self.ui.export_result(None, '&QGIS')
        self.assertEqual(
            len(self.ui.export_result_window.result.toPlainText().split('\n')), 3)
        self.assertIn('MULTILINESTRING',
                      self.ui.export_result_window.result.toPlainText())
        self.ui.export_result_window.close()
        return

    #----------------------------------------------------------------------
    def test_export_markdown(self):
        """export result of SQL query execution to a Markdown text"""
        self._prepare_for_export()

        self.ui.export_result(None, '&Markdown')
        self.assertEqual(
            len(self.ui.export_result_window.result.toPlainText().split('\n')), 5)
        self.ui.export_result_window.close()
        return

    #----------------------------------------------------------------------
    def test_export_pandas(self):
        """export result of SQL query execution to a pandas data frame"""
        self._prepare_for_export()

        self.ui.export_result(None, '&DataFrame')
        self.assertIn('.csv', self.ui.export_result_window.result.toPlainText())
        self.ui.export_result_window.close()
        return

    #----------------------------------------------------------------------
    def test_export_arcmap(self):
        """export result of SQL query execution to arcpy code to use in ArcMap"""
        self._prepare_for_export()

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
        # TODO: implement test
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
        self.assertEqual(self.tab.table.table_data.number_layer_rows, 3)
        self.assertEqual(self.tab.table.table_data.columnCount(), 3)
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
        self.tab.run_query()
        self.assertTrue(self.tab.table.isVisible())
        self.assertEqual(self.tab.table.table_data.number_layer_rows, 3)
        self.assertEqual(self.tab.table.table_data.columnCount(), 1)
        return

    #----------------------------------------------------------------------
    def test_execute_sql_query_selection(self):
        """test executing only selected part of the SQL query"""
        self.tab = self._add_new_query_tab()
        sql_query_string = 'SELECT name FROM streets LIMIT 3\n UPDATE'
        self._prepare_query_text(sql_query_string)
        self.tab.run_query()
        self.assertTrue(self.tab.errors_panel.isVisible())
        self.assertIn('UPDATE', self.tab.errors_panel.toPlainText())

        cur = self.tab.query.textCursor()
        cur.setPosition(0)
        cur.setPosition(32, QTextCursor.KeepAnchor)
        self.tab.query.setTextCursor(cur)
        self.assertEqual(self.tab.query.textCursor().selectedText(),
                         sql_query_string[:32])

        self.tab.run_query()
        self.assertFalse(self.tab.errors_panel.isVisible())
        self.assertTrue(self.tab.table.isVisible())
        self.assertEqual(self.tab.table.table_data.number_layer_rows, 3)
        self.assertEqual(self.tab.table.table_data.columnCount(), 1)
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
        #self.tab.query.textCursor().charFormat().font().Bold
        return

    #----------------------------------------------------------------------
    def test_copy_result_table_row(self):
        """test select and copy a row into a clipboard"""
        self.tab = self._add_new_query_tab()
        sql_query_string = 'SELECT name, type FROM streets ORDER BY name desc, type desc LIMIT 1'
        self._prepare_query_text(sql_query_string)
        self._execute_sql(sql_query_string)

        self.tab.table.view.model().fetchMore()  # need to load into `rows` from OGR layer
        self.assertEqual(len(self.tab.table.view.model().rows), 1)
        self.tab.table.view.selectRow(0)

        QTest.keyPress(self.tab.table.view, Qt.Key_C, Qt.ControlModifier)
        cp = self.app.clipboard().text()
        parsed_cp = [i.split('\t') for i in cp.split('\n') if i]
        self.assertEqual(parsed_cp[0], ['NAME', 'TYPE'])
        self.assertEqual(parsed_cp[1], ['Zwicky Ave', 'residential'])
        return

    #----------------------------------------------------------------------
    def test_copy_result_table_cell(self):
        """test select and copy a column cell value into a clipboard"""
        self.tab = self._add_new_query_tab()
        sql_query_string = 'SELECT name, type FROM streets ORDER BY name desc, type desc LIMIT 1'
        self._prepare_query_text(sql_query_string)
        self._execute_sql(sql_query_string)

        self.tab.table.view.model().fetchMore()  # need to load into `rows` from OGR layer
        tm = self.tab.table.view.model()
        sm = self.tab.table.view.selectionModel()
        idx = tm.index(0, 0, QModelIndex())
        sm.select(idx, QItemSelectionModel.Select)

        QTest.keyPress(self.tab.table.view, Qt.Key_C, Qt.ControlModifier)
        cp = self.app.clipboard().text()
        self.assertEqual(cp, 'Zwicky Ave')
        return

    #----------------------------------------------------------------------
    def test_filling_toc(self):
        """test fill the toc with gdb tables and their columns"""
        self.tab = self._add_new_query_tab()
        sql_query_string = 'SELECT name FROM streets LIMIT 3'
        self._execute_sql(sql_query_string)
        self.tab._set_gdb_items_highlight()
        self.tab._fill_toc()
        self.assertEqual(
            sorted([i.lower() for i in self.tab.gdb_items]),
            sorted([
                self.tab.toc.topLevelItem(i).text(0).lower()
                for i in range(self.tab.toc.topLevelItemCount())
            ]))
        return

    #----------------------------------------------------------------------
    def test_expand_collapse_toc(self):
        """test expand and collapse all items in the toc"""
        self.tab = self._add_new_query_tab()
        sql_query_string = 'SELECT name FROM streets LIMIT 3'
        self._execute_sql(sql_query_string)
        self.tab._set_gdb_items_highlight()
        self.tab._fill_toc()
        self.ui.toc_expand_all()
        self.assertTrue(
            all([
                self.tab.toc.topLevelItem(i).isExpanded()
                for i in range(self.tab.toc.topLevelItemCount())
            ]))
        self.ui.toc_collapse_all()
        self.assertTrue(not any([
            self.tab.toc.topLevelItem(i).isExpanded()
            for i in range(self.tab.toc.topLevelItemCount())
        ]))
        return

    #----------------------------------------------------------------------
    def test_changing_sql_dialects(self):
        """test choosing OGR SQL dialect and execute the SQL query with
        unsupported keyword and then change back to SQLite"""
        self.tab = self._add_new_query_tab()
        sql_query_string = 'SELECT name FROM streets'
        self.tab.gdb_sql_dialect_combobox.setCurrentText('OGRSQL')
        self._execute_sql(sql_query_string)
        self.assertEqual(self.tab.table.table_data.number_layer_rows, 19091)

        sql_query_string = 'select st_x(shape) from homicides limit 5'
        self._execute_sql(sql_query_string)
        self.assertIn('Undefined function', self.tab.errors_panel.toPlainText())
        self.tab.gdb_sql_dialect_combobox.setCurrentText('SQLite')
        self._execute_sql(sql_query_string)
        self.assertEqual(self.tab.table.table_data.number_layer_rows, 5)
        return

    #----------------------------------------------------------------------
    def _prepare_query_text(self, sql_query):
        """put SQL query string """
        self.tab.gdb = self.local_gdb
        sql_query_string = sql_query
        self.tab.query.setText(sql_query_string)
        return

    #----------------------------------------------------------------------
    def _prepare_for_export(self):
        """prepare data for exporting the result set"""

        self.assertEqual(self._get_tabs_count(), 0)
        self.tab = self._add_new_query_tab()
        self.assertEqual(self._get_tabs_count(), 1)

        self.tab.gdb = (self.local_gdb)
        self.tab = self.ui.tab_widget.currentWidget()
        self.tab.query.setPlainText(
            'SELECT Name, Type, Oneway, Shape FROM streets LIMIT 3')

        self.tab.run_query()
        self.assertEqual(self.tab.table.table_data.number_layer_rows, 3)
        self.assertEqual(self.tab.table.table_data.columnCount(), 4)

        return

    #----------------------------------------------------------------------
    def _execute_sql(self, sql, user_gdb=None):
        """execute SQL query in the current tab"""
        self.tab = self.ui.tab_widget.currentWidget()
        if user_gdb:
            self.tab.gdb = GDB(user_gdb)
        else:
            self.tab.gdb = self.local_gdb
        self.tab.query.setPlainText(sql)
        self.tab.run_query()
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
