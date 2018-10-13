# -*- coding: UTF-8 -*-
"""Geodatabase class representing a file geodatabase object."""

import ogr
ogr.UseExceptions()


########################################################################
class Geodatabase(object):
    """File geodatabase object."""

    # ----------------------------------------------------------------------
    def __init__(self, path):
        """Initialize Geodatabase class with basic properties."""
        self.path = path
        self.ds = None
        return

    # ----------------------------------------------------------------------
    def get_items(self):
        """Get list of tables and feature classes inside a file gdb."""
        ds = ogr.Open(self.path, 0)
        return list({
            ds.GetLayerByIndex(i).GetName()
            for i in range(0, ds.GetLayerCount())
        })

    # ----------------------------------------------------------------------
    def get_schemas(self):
        """Get all tables and feature classes inside a file gdb.

        Return dict { layer_name: [ {columns_name: column_type} ] }
        """
        ds = ogr.Open(self.path, 0)
        schemas = {}
        for item in self.get_items():
            cols_names = []
            lyr = ds.GetLayerByName(item)
            lyr_defn = lyr.GetLayerDefn()
            geom_col = lyr.GetGeometryColumn()
            cols_names.extend([col.GetName() for col in lyr.schema])
            field_types = {
                col_name: lyr_defn.GetFieldDefn(
                    lyr_defn.GetFieldIndex(col_name)).GetTypeName()
                for col_name in cols_names
            }
            if geom_col:
                field_types[geom_col] = 'Geometry'
            schemas[item] = field_types
        return schemas

    # ----------------------------------------------------------------------
    def is_valid(self):
        """Check if .gdb folder provided by user is a valid file gdb."""
        try:
            ds = ogr.Open(self.path, 0)
        except BaseException:
            return False

        if ds:
            ds.Destroy()
            return True
        return False

    # ----------------------------------------------------------------------
    def open_connection(self):
        """Open geodatabase for reading.

        Need to keep open for interacting with layers returned after
        running the `ExecuteSQL` method.
        """
        self.ds = ogr.Open(self.path, 0)
        return

    # ----------------------------------------------------------------------
    def close_connection(self):
        """Close connection to geodatabase."""
        if self.ds:
            self.ds.Destroy()
        return

    # ----------------------------------------------------------------------
    def execute_sql(self, query, dialect='sqlite'):
        """Execute SQL query against a geodatabase using a `ExecuteSQL` method.

        http://gdal.org/python/osgeo.ogr.DataSource-class.html#ExecuteSQL.
        """
        # TODO trigger using spatial index in SQLite?
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
