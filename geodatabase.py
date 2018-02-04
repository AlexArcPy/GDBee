# -*- coding: UTF-8 -*-
'''Geodatabase class representing a file geodatabase object'''

import ogr
ogr.UseExceptions()


########################################################################
class Geodatabase(object):
    """File geodatabase object"""

    #----------------------------------------------------------------------
    def __init__(self, path):
        """Constructor"""
        self.path = path
        self.ds = None
        return

    #----------------------------------------------------------------------
    def get_items(self):
        """get list of tables and feature classes inside a file gdb"""
        ds = ogr.Open(self.path, 0)
        return list(
            set([ds.GetLayerByIndex(i).GetName() for i in range(0, ds.GetLayerCount())]))

    #----------------------------------------------------------------------
    def get_schemas(self):
        """get dict { layer_name: [columns_names] }
        for all tables and feature classes inside a file gdb"""
        ds = ogr.Open(self.path, 0)
        schemas = {}
        for item in self.get_items():
            cols_names = []
            lyr = ds.GetLayerByName(item)
            geom_col = lyr.GetGeometryColumn()
            cols_names.extend([col.GetName() for col in lyr.schema])
            cols_names += [geom_col] if geom_col is not '' else []
            schemas[item] = cols_names
        return schemas

    #----------------------------------------------------------------------
    def is_valid(self):
        """check if .gdb folder provided by user is a valid file gdb"""
        try:
            ds = ogr.Open(self.path, 0)
        except:
            return False

        if ds:
            ds.Destroy()
            return True
        return False

    #----------------------------------------------------------------------
    def open_connection(self):
        """open geodatabase for reading; need to keep open for interacting with
        layers returned after running the `ExecuteSQL` method"""
        self.ds = ogr.Open(self.path, 0)
        return

    #----------------------------------------------------------------------
    def close_connection(self):
        """close connection to geodatabase"""
        if self.ds:
            self.ds.Destroy()
        return

    #----------------------------------------------------------------------
    def execute_sql(self, query, dialect='sqlite'):
        """Execute SQL query against a geodatabase using a `ExecuteSQL` method.
        Read more at http://gdal.org/python/osgeo.ogr.DataSource-class.html#ExecuteSQL"""
        #TODO trigger using spatial index in SQLite?
        try:
            if not dialect:
                dialect = 'sqlite'
            res, errors = None, None
            do_commit_transaction = True
            if dialect.lower() == 'sqlite':
                do_commit_transaction = False
            res = self.ds.ExecuteSQL(query, dialect=dialect)
            if do_commit_transaction:
                res.CommitTransaction()
        except Exception as err:
            errors = err.args[0]

        return res, errors
