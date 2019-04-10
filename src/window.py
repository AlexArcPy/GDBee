# -*- coding: UTF-8 -*-
"""Windows within the application."""

import io
import os
import tempfile

import pkg_resources
try:
    pkg_resources.get_distribution('tabulate')
    from tabulate import tabulate
except Exception:
    pkg_resources.DistributionNotFound
    tabulate_found = False
else:
    tabulate_found = True

from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QTextEdit,
                             QApplication)
from PyQt5.Qt import Qt
from PyQt5.QtGui import QIcon, QKeySequence
from tab_widget import TabWidget

from cfg import project_name, test_mode


########################################################################
class ExportResultWindow(QMainWindow):
    """Window with the result of exporting the data."""

    def __init__(self, parent=None):
        """Initialize ExportResultWindow with basic properties."""
        super(ExportResultWindow, self).__init__(parent)
        self.result = QTextEdit()
        self.result.setTabStopWidth(20)
        font = self.result.font()
        font.setPointSize(11)
        self.result.setFont(font)
        self.setWindowTitle('Export result')
        self.setCentralWidget(self.result)
        self.setGeometry(300, 300, 900, 300)
        return


########################################################################
class Window(QMainWindow):
    """Window that contains the tab container."""

    # ----------------------------------------------------------------------
    def __init__(self, parent=None):
        """Initialize Window with basic properties."""
        super(Window, self).__init__(parent)
        self.setWindowTitle(project_name)
        self.setWindowIcon(QIcon('logo.png'))
        self.statusBar().showMessage('')

        menu = self.menuBar()

        # File menu
        file_menu = menu.addMenu('&File')
        menus = [
            ('&New query', 'Ctrl+N', self.open_new_tab, False),
            ('&Save query', 'Ctrl+S', self.save_query_to_file, False),
            ('&Open query', 'Ctrl+O', self.open_query_from_file, False),
        ]
        for cmd_name, shortcut, connected_func, separator in menus:
            action = QAction(cmd_name, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(connected_func)
            file_menu.addAction(action)
            if separator:
                file_menu.addSeparator()

        # TOC menu
        toc_menu = menu.addMenu('&Schemas')
        toc_hide_action = QAction('&Hide/show panel', self)
        toc_hide_action.setShortcuts(QKeySequence('F1'))
        toc_hide_action.triggered.connect(self._do_toc_hide_show)

        toc_expand_action = QAction('&Expand all', self)
        toc_expand_action.triggered.connect(self.toc_expand_all)

        toc_collapse_action = QAction('&Collapse all', self)
        toc_collapse_action.triggered.connect(self.toc_collapse_all)

        toc_menu.addAction(toc_hide_action)
        toc_menu.addAction(toc_expand_action)
        toc_menu.addAction(toc_collapse_action)

        # Result menu
        result_menu = menu.addMenu('&Result')
        result_export_menu = result_menu.addMenu('Export to')
        result_export_menu.setToolTipsVisible(True)

        export_action_qgis = result_export_menu.addAction('&QGIS')
        export_action_qgis.setToolTip(
            'Get plain WKT to use with the QuickWKT plugin')

        export_action_arc = result_export_menu.addAction('&ArcMap')
        export_action_arc.setToolTip('Get arcpy code to create in_memory layer')

        export_action_df = result_export_menu.addAction('&DataFrame')
        export_action_df.setToolTip(
            'Get Python code to create a pandas df using a temp csv file')

        export_action_md = result_export_menu.addAction('&Markdown')
        export_action_md.setToolTip('Get table formatted in Markdown')

        option = None
        export_action_qgis.triggered.connect(
            lambda evt, arg=option: self.export_result(
                evt, export_action_qgis.text()))
        export_action_arc.triggered.connect(
            lambda evt, arg=option: self.export_result(
                evt, export_action_arc.text()))
        export_action_df.triggered.connect(
            lambda evt, arg=option: self.export_result(
                evt, export_action_df.text()))
        export_action_md.triggered.connect(
            lambda evt, arg=option: self.export_result(
                evt, export_action_md.text()))

        settings_menu = menu.addMenu('&Settings')
        settings_menu.setToolTipsVisible(True)
        self.do_include_geometry = QAction(
            'Include geometry column in query result set', self, checkable=True)
        self.do_include_geometry.setToolTip(
            """Will include WKT representation of
            geometry column in the result table""")
        settings_menu.addAction(self.do_include_geometry)
        self.do_include_geometry.setChecked(True)

        self.tab_widget = TabWidget()
        self.setCentralWidget(self.tab_widget)
        self.setGeometry(100, 100, 1000, 900)
        self.show()

        self.export_result_window = None
        return

    # ----------------------------------------------------------------------
    def export_result(self, evt, option):
        """Export result set into an output format."""
        current_tab = self.tab_widget.widget(self.tab_widget.currentIndex())
        try:
            if not test_mode:
                if not current_tab.table.table_data.rowCount():
                    raise
            else:
                if not current_tab.table.table_data.number_layer_rows:
                    raise
        except Exception:
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        df = current_tab.table.get_selected_data_as_df()

        if not self.export_result_window:
            self.export_result_window = ExportResultWindow()

        if option == '&QGIS':
            if self.window().tab_widget.currentWidget(
            ).geometry_isin_query and self.window(
            ).do_include_geometry.isChecked():
                s = '\n'.join(df[df.columns[-1]].tolist())
                self.export_result_window.result.setText(s)
            else:
                self.export_result_window.result.setText('')

        if option == '&ArcMap':
            if self.window().tab_widget.currentWidget(
            ).geometry_isin_query and self.window(
            ).do_include_geometry.isChecked():
                # TODO: get the fields data along with the geometries/dump csv
                snippet = self._get_arcmap_snippet(
                    geoms=df[df.columns[-1]].tolist())
                self.export_result_window.result.setText(snippet)
            else:
                self.export_result_window.result.setText('')

        if option == '&DataFrame':
            out_csv = os.path.join(tempfile.gettempdir(), 'data.csv')
            df.to_csv(out_csv, sep=';')
            s = '{0}{1}'.format(
                'import pandas as pd\n',
                'df = pd.read_csv(r"{out_csv}", sep=";", index_col=0)'.format(
                    out_csv=out_csv))
            self.export_result_window.result.setText(s)

        if option == '&Markdown':
            if not tabulate_found:
                self.export_result_window.result.setText(
                    'Tabulate package is not installed.\n'
                    'Get it from https://pypi.python.org/pypi/tabulate')
            else:
                s = tabulate(
                    df, headers='keys', tablefmt='pipe', floatfmt='.4f')
                if len(df) > 1000:
                    out_md = os.path.join(tempfile.gettempdir(), 'data.md')
                    with io.open(out_md, 'w', encoding='utf-8') as f:
                        f.write(s)
                    self.export_result_window.result.setText(
                        'Markdown file is saved at {0}'.format(out_md))
                else:
                    self.export_result_window.result.setText(s)

        QApplication.restoreOverrideCursor()
        self.export_result_window.show()
        return

    # ----------------------------------------------------------------------
    def open_new_tab(self):
        """Open a new query tab."""
        self.tab_widget.add_tab_page()
        return

    # ----------------------------------------------------------------------
    def save_query_to_file(self):
        """Save query of the focused tab."""
        current_tab = self.tab_widget.widget(self.tab_widget.currentIndex())
        if current_tab:
            tab_text = current_tab.query.document().toPlainText()
            if tab_text:
                name = QFileDialog.getSaveFileName(
                    self, 'Save as new file', filter='All Files (*)')
                if name[0]:
                    with io.open(name[0], 'w', encoding='utf-8') as f:
                        f.write(tab_text)
                        f.close()
        return

    # ----------------------------------------------------------------------
    def open_query_from_file(self):
        """Open text file with query into the focused tab."""
        name = QFileDialog.getOpenFileName(
            self, 'Open a query text file', filter='All Files (*)')
        if name[0]:
            with io.open(name[0], 'r', encoding='utf-8') as f:
                query = f.readlines()
                f.close()
                self.open_new_tab()
                current_tab = self.tab_widget.widget(
                    self.tab_widget.currentIndex())
                current_tab.query.document().setPlainText(''.join(query))
        return

    # ----------------------------------------------------------------------
    def toc_expand_all(self):
        """Expand all items in the schemas panel."""
        try:
            self.tab_widget.currentWidget().toc.expandAll()
        except Exception:
            return

    # ----------------------------------------------------------------------
    def toc_collapse_all(self):
        """Collapse all items in the schemas panel."""
        try:
            self.tab_widget.currentWidget().toc.collapseAll()
        except Exception:
            return

    # ----------------------------------------------------------------------
    def _do_toc_hide_show(self):
        """Hide or show toc panel."""
        try:
            self.tab_widget.currentWidget()._do_toc_hide_show()
        except Exception:
            pass

    # ----------------------------------------------------------------------
    def _get_arcmap_snippet(self, geoms):
        """Get arcpy code with received table rows ready to load into ArcMap."""
        gp_call = "arcpy.CopyFeatures_management(geoms,'in_memory\GDBeeLayer')"
        base_string = '{geoms}{for_loop}{build_geom}{append_geom}{copy_feats}'
        snippet = base_string.format(
            geoms='geoms = []\n',
            for_loop='for wkt_str in {0}:\n'.format(geoms),
            build_geom='\tg = arcpy.FromWKT(wkt_str)\n',
            append_geom='\tgeoms.append(g)\n',
            copy_feats=gp_call,
        )
        return snippet
