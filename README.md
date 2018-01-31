# Overview

`GDBee` is a PyQt5 desktop application which you can use to write and execute SQL queries against tables and feature classes stored inside an Esri file geodatabase. It provides a tabbed interface which lets you connect to multiple geodatabases within a single session. It has a rich code editor featuring auto-completion (with suggestions), syntax highlight, and result set export.

If you are a QGIS Desktop user, you are already able to execute SQL against file geodatabases using [QGIS DBManager plugin](https://docs.qgis.org/2.14/en/docs/user_manual/plugins/plugins_db_manager.html), but `GDBee` has some extra features that the DBManager is missing (for instance, you do not need to add your datasets as layers first and you can choose to copy individual cells instead of the whole row) from the result table.

<p align="center">
  <img src="https://user-images.githubusercontent.com/7373268/35639024-1e74b39c-06b9-11e8-994c-837a1713fc64.png" alt="GDBee window"/>
</p>

## History

This project has started as an experimental playground to see what functionality PyQt provides. As I spent more time working with PyQt, I have started wondering what it would take to build a simple desktop application. Because I often find myself in need of querying a file geodatabase's datasets, I have decided to build a GUI-based SQL editor that would let me execute SQL queries against a table or a feature class and draw the result set in a table form for further visual inspection. I have thought that other GIS users and developers may find this application useful and I therefore have decided to start a GitHub repository to let others take advantage of my work.

## Features

* Working with multiple geodatabases using multiple tabs (single geodatabase connection per tab)
* Exporting result sets into various formats (`WKT` strings to paste into QGIS using [QuickWKT plugin](https://plugins.qgis.org/plugins/QuickWKT/), `arcpy` code to paste into ArcMap Python window, `pandas` data frame via `.csv` file (which can be taken into `geopandas`), and Markdown table via `.md` file or plain text)
* Executing SQL query with respect to the user selection (only selected text is executed)
* Loading/saving SQL queries from and to text files on disk
* Convenient keyboard shortcuts for query execution (`F5` and `Ctrl-Enter`) and tab interaction (`Ctrl-N` and `Ctrl-W` for opening and closing tabs)
* Copying data from the result set table (either individual cell values or row(s) with the headers preserved) - ready to paste properly into an Excel sheet
* Choosing whether you want to have geometry column in the result set as WKT

## Limitations

* All queries should target datasets stored within a single geodatabase; you won't be able to run this query:

```sql
SELECT * FROM DB1.Parcels WHERE Parcels.ID in (SELECT ID FROM DB2.Parcels)
```

* The application can be used only for selecting existing data and creating new data within the application session; you won't be able to execute any `UPDATE`, `INSERT`, or `DELETE` queries in the current version. If you want to save the generated shapes (for instance, as a result of buffering or getting vertices of polygons as points), you can use the export functionality to load the WKT representation of the shapes into an ArcMap or QGIS layer.

## Requirements

* Python 3.5
* `GDAL` 2.1.0
* `PyQt5`
* `pandas`
* `tabulate` (optional, used for exporting result set into a markdown table)

Tested against:

```sql
select geos_version() --3.6.2-CAPI-1.10.2 999999
select proj4_version() --Rel. 4.9.3, 15 August 2016
select spatialite_version() --4.3.0-RC1
```

```python
osgeo.gdal.VersionInfo() # '2010400'
```

### Installation

You don't need to install anything apart from `PyQt` and `GDAL` (and `pandas` which is used for exporting) in order to be able to run the application. All of these can be installed using [Anaconda Navigator](https://docs.continuum.io/anaconda/navigator/) which is arguably the easiest way to proceed.

I've tried various combinations to get PyQt5 and GDAL working happily together with Python 2.7 but haven't managed this. However, if you do have a Python 2.7 environment with the requirements satisfied, by all means go ahead and use it.

To run the application, just run the `main.py` file using the right Python interpreter.

## Target audience

You may find this PyQt desktop application useful if:

* You would like to be able to interrogate your file geodatabase datasets using SQL (instead of Python-based interface such as Esri `arcpy` or open-source `ogr`)
* You are an ArcGIS user that does not want to have QGIS Desktop installed just to be able to execute SQL against a file geodatabase
* You use SQL on a daily basis working with spatial databases (such as PostgreSQL or Microsoft SQL Server) and want to be able to execute ad hoc SQL queries against file geodatabase datasets without loading them into a proper DBMS database
* You already have a lot SQL code targeting tables stored in a DBMS spatial database and you would like to be able to reuse this code when targeting a file geodatabase

## Using SQL for querying file geodatabases

If you are an ArcGIS user, you have already used SQL for querying your file geodatabase datasets when using the `Select By Attributes` and `Select By Location` dialog windows or `Select Layer By Attributes`, `Select Layer By Location`, `Make Feature Layer` or `Select` geoprocessing tools. You have supplied a `where` clause specifying what features or rows you would like to select. This can be done simply to see what data match your query or to perform some analysis on the subset of your data. The querying functionality available through these tools is somewhat limited, though, because you will not be able to take advantage of rich SQL operations such as grouping your data, joining multiple tables, or using spatial SQL functions.

Open source GIS users have better tools for querying file geodatabases using SQL; [QGIS DBManager plugin](https://docs.qgis.org/2.8/en/docs/training_manual/databases/db_manager.html) does provide an excellent interface for executing SQL queries against map layers added from a file geodatabase. However, this requires installing QGIS Desktop software and adding all the datasets you would like to participate in the SQL query into a map. Also, there are no tools to quickly export the result set in a suitable format.

Esri does provide [File Geodatabase C++ API for Windows, MacOS and Linux](https://github.com/Esri/file-geodatabase-api), however it also has a number of limitations; for instance, SQL joins are not supported and you would need to have Microsoft Visual Studio for development (gcc/clang on Linux). You would also need to bind the API to your own language of choice since only .NET bindings are included.

Because Python is widely used in the GIS community, I thought it would make sense to take advantage of Python bindings of `GDAL` (via [`GEOS`](https://trac.osgeo.org/geos)) to be able to connect to a file geodatabase and execute SQL queries. Working with a file geodatabase via `GEOS` makes it possible to take advantage of SQL spatial functions that are otherwise inaccessible to an ArcGIS user.

## Examples of executing SQL queries against file geodatabase using `GDAL`

In this section, you find just a few sample SQL queries that have been executed in the `GDBee` against an Esri file geodatabase containing datasets accessible via [PostGIS workshop materials by Boundless](http://workshops.boundlessgeo.com/postgis-intro/index.html) which can be downloaded from [this link](http://files.boundlessgeo.com/workshopmaterials/postgis-workshop-201401.zip).

The queries and the result sets are here to show you the power of SQL when working with file geodatabases. You can learn more about using SQL for querying file geodatabases in the Esri documentation available at [Use SQL for reporting and analysis on file geodatabases](http://desktop.arcgis.com/en/arcmap/latest/manage-data/administer-file-gdbs/sql-reporting-and-anlysis-file-geodatabases.htm). The full list of the spatial and non-spatial functions available for a `GDAL` user is listed in the [SpatialLite documentation](http://www.gaia-gis.it/spatialite-2.4.0/spatialite-sql-2.4.html). Nearly all SQL functions are available for a `GDAL` user (look for the `GEOS` column).

The SQL queries are executed with the help of `GDAL` Python bindings using the [`ExecuteSQL()`](http://gdal.org/python/osgeo.ogr.DataSource-class.html#ExecuteSQL) method (mind that `SQLITE` dialect is being used). The result set returned is post-processed to include the abridged `WKT` representation of the geometries. The result sets have been converted subsequently into a `markdown` table for displaying in this guide.

More examples can be found in the [samples document](https://github.com/AlexArcPy/GDBee/blob/master/docs/sample_queries.md).

### Non-spatial queries

#### Counting non-white population in ten most populated census blocks

```sql
SELECT
    BLKID
    , BORONAME
    , CAST(POPN_TOTAL AS INTEGER) AS TotalPop
    , CAST(POPN_WHITE AS INTEGER) AS WhitePop
    , CAST(POPN_TOTAL - POPN_WHITE AS INTEGER) AS NonWhitePopulation
FROM
    census_blocks
ORDER BY
    POPN_TOTAL DESC
LIMIT
    5
```

|    |           BLKID | BORONAME   |   TotalPop |   WhitePop |   NonWhitePopulation |
|---:|----------------:|:-----------|-----------:|-----------:|---------------------:|
|  0 | 360050001001000 | The Bronx  |       8634 |       1242 |                 7392 |
|  1 | 360610238011009 | Manhattan  |       4970 |       2704 |                 2266 |
|  2 | 360810797012000 | Queens     |       4563 |        436 |                 4127 |
|  3 | 360610155006000 | Manhattan  |       4067 |       3507 |                  560 |
|  4 | 360471034001004 | Brooklyn   |       3918 |        605 |                 3313 |

#### Find total population of each borough using `HAVING`

```sql
SELECT
    BORONAME
    , SUM(POPN_TOTAL) AS TotalPop
FROM
    census_blocks
GROUP BY
    BORONAME
HAVING
    SUM(POPN_TOTAL) > 1500000
ORDER BY
    TotalPop DESC
```

|    | BORONAME   |     TotalPop |
|---:|:-----------|-------------:|
|  0 | Brooklyn   | 2504700.0000 |
|  1 | Queens     | 2230621.0000 |
|  2 | Manhattan  | 1585873.0000 |

### Spatial queries

#### Find all crime incidents located within 300 feet from a certain subway station (`ST_Distance`)

```sql
SELECT *
FROM
    homicides
WHERE
    ST_Distance(Shape, (SELECT shape FROM subway_stations WHERE name = 'Essex St')) < 300
```

|    | INCIDENT_D          | BORONAME   |   NUM_VICTIM | PRIMARY_MO       |        ID | WEAPON   | LIGHT_DARK   |      YEAR | Shape                            |
|---:|:--------------------|:-----------|-------------:|:-----------------|----------:|:---------|:-------------|----------:|:---------------------------------|
|  0 | 2008/05/13 00:00:00 | Manhattan  |            1 |                  |  144.0000 | knife    | D            | 2008.0000 | POINT (585477.5157 4508066.903)  |
|  1 | 2003/01/12 00:00:00 | Manhattan  |            1 | ROBBERY/BURGLARY |  721.0000 | gun      |              | 2003.0000 | POINT (585252.013 4507899.3078)  |
|  2 | 2003/06/10 00:00:00 | Manhattan  |            1 | DRUGS            |  728.0000 | gun      |              | 2003.0000 | POINT (585747.6144 4507957.7557) |
|  3 | 2004/10/25 00:00:00 | Manhattan  |            1 | DOMESTIC         | 1404.0000 | other    |              | 2004.0000 | POINT (585688.4776 4508016.8018) |
|  4 | 2005/01/27 00:00:00 | Manhattan  |            1 | ROBBERY/BURGLARY | 1553.0000 | gun      |              | 2005.0000 | POINT (585710.8339 4508019.2805) |
|  5 | 2005/08/17 00:00:00 | Manhattan  |            1 | REVENGE          | 1825.0000 | knife    |              | 2005.0000 | POINT (585404.4815 4508200.4864) |
|  6 | 2007/07/06 00:00:00 | Manhattan  |            1 | DISPUTE          | 2834.0000 | knife    | D            | 2007.0000 | POINT (585305.7312 4508053.368)  |
|  7 | 2011/04/10 00:00:00 | Manhattan  |            1 |                  | 4171.0000 | gun      |              | 2011.0000 | POINT (585724.1624 4508111.4603) |

#### Find neighborhoods with the largest number of crimes committed (count number of homicides in each neighborhood) (`ST_Contains`)

```sql
SELECT
    Polys.Name AS NeighborhoodName
    , Count(*) AS CrimeCount
FROM
  Homicides AS Points
JOIN
  Neighborhoods AS Polys
ON
    ST_Contains(Polys.Shape, Points.Shape) = 1
AND
    Points.YEAR in (2008, 2009, 2010)
GROUP BY
    Polys.Name
ORDER BY
    CrimeCount DESC
LIMIT 10
```

|    | NeighborhoodName         |   CrimeCount |
|---:|:-------------------------|-------------:|
|  0 | Bedford-Stuyvesant       |          113 |
|  1 | South Bronx              |           66 |
|  2 | Brownsville              |           50 |
|  3 | East Brooklyn            |           43 |
|  4 | Harlem                   |           41 |
|  5 | Jamaica                  |           37 |
|  6 | Tremont                  |           30 |
|  7 | Wakefield-Williamsbridge |           29 |
|  8 | Mott Haven               |           27 |
|  9 | Fort Green               |           25 |

### New functionality under consideration

* Tree-view into all tables and columns in the database (SSMS like)
* FileGDB API to add editing mode of geodatabase ([supported by ogr](http://www.gdal.org/ogr_sql_sqlite.html))

### Issues

Did you find a bug? Do you think there is some other functionality that should be added? Please let me know by submitting an issue.

### Licensing

MIT
