# -*- coding: UTF-8 -*-
'''Table with result set'''

import os
import pandas as pd

from PyQt5.Qt import QTableWidget, QKeySequence, QApplication, QTextEdit
from PyQt5.Qt import QMainWindow


########################################################################
class ResultTable(QTableWidget):
    """Table with result set returned by SQL query"""

    #----------------------------------------------------------------------
    def __init__(self, parent=None):
        """Constructor"""
        # TODO improve performance using
        # https://stackoverflow.com/a/12093506/3346915 ?
        super(ResultTable, self).__init__(parent)
        return

    #----------------------------------------------------------------------
    def keyPressEvent(self, evt):
        """overriding built-in method to copy the rows into clipboard"""
        # TODO: scroll the table using PageDown and PageUp keys

        if evt.matches(QKeySequence.Copy):
            clipboard = QApplication.clipboard()
            sel = self.selectedRanges()

            # user is trying to copy a single cell value; no need for cols headers
            if sel[0].leftColumn() == sel[0].rightColumn() and sel[0].bottomRow(
            ) == sel[0].topRow():
                data = ''
            else:
                data = "\t".join([
                    str(self.horizontalHeaderItem(i).text())
                    for i in range(sel[0].leftColumn(), sel[0].rightColumn() + 1)
                ])
                data += '\n'

            for row in range(sel[0].topRow(), sel[0].bottomRow() + 1):
                for col in range(sel[0].leftColumn(), sel[0].rightColumn() + 1):
                    try:
                        item = self.item(row, col)
                        if hasattr(item, '_wkt'):
                            data += item._wkt + "\t"
                        else:
                            data += item.text() + "\t"

                    except AttributeError:
                        data += "\t"
                data = data[:-1] + "\n"
            clipboard.setText(data)

    #----------------------------------------------------------------------
    def get_selected_data_as_df(self):
        """get selected data as pandas data frame"""
        number_of_rows = self.rowCount()
        number_of_columns = self.columnCount()

        if number_of_columns and number_of_rows:
            pd.set_option('display.float_format', lambda x: '%.3f' % x)

            rows = [[
                self.item(i, j).data(0)
                if not hasattr(self.item(i, j), '_wkt') else self.item(i, j)._wkt
                for j in range(number_of_columns)
            ] for i in range(number_of_rows)]

            df = pd.DataFrame.from_records(
                rows, columns=self.columns_names, index=range(1, number_of_rows + 1))
            return df
