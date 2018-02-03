# Overview

In this file, you find a few sample SQL queries that have been executed in the `GDBee` application against an Esri file geodatabase containing datasets accessible via [PostGIS workshop materials by Boundless](http://workshops.boundlessgeo.com/postgis-intro/index.html) which can be downloaded from [this link](http://files.boundlessgeo.com/workshopmaterials/postgis-workshop-201401.zip).

## Sample queries

The queries and the result sets are here to show you the power of SQL when working with file geodatabases. More samples will be added.

### Non-spatial queries

#### Select all the data about first five yellow route subway stations

```sql
SELECT * FROM subway_stations
WHERE color = 'Yellow'
LIMIT 5
```

|    |   OBJECTID |   ID | NAME         | ALT_NAME   | CROSS_ST   | LONG_NAME                    | LABEL              | BOROUGH   | NGHBHD   | ROUTES   | TRANSFERS   | COLOR   | EXPRESS   | CLOSED   | Shape                            |
|---:|-----------:|-----:|:-------------|:-----------|:-----------|:-----------------------------|:-------------------|:----------|:---------|:---------|:------------|:--------|:----------|:---------|:---------------------------------|
|  0 |          1 |  376 | Cortlandt St |            | Church St  | Cortlandt St (R,W) Manhattan | Cortlandt St (R,W) | Manhattan |          | R,W      | R,W         | YELLOW  |           |          | POINT (583521.8544 4507077.8626) |
|  1 |         76 |  430 | 18th Ave     |            | 64th St    | 18th Ave (N) Brooklyn        | 18th Ave (N)       | Brooklyn  |          | N        | N           | YELLOW  |           |          | POINT (585487.2188 4497065.7728) |
|  2 |         78 |  431 | 20th Ave     |            | 64th St    | 20th Ave (N) Brooklyn        | 20th Ave (N)       | Brooklyn  |          | N        | N           | YELLOW  |           |          | POINT (585859.7682 4496776.831)  |
|  3 |         83 |  408 | 45th St      |            | 4th Ave    | 45th St (R) Brooklyn         | 45th St (R)        | Brooklyn  |          | R        | R           | YELLOW  |           |          | POINT (583729.1489 4500294.2976) |
|  4 |         86 |  409 | 53rd St      |            | 4th Ave    | 53rd St (R) Brooklyn         | 53rd St (R)        | Brooklyn  |          | R        | R           | YELLOW  |           |          | POINT (583341.0729 4499794.1689) |

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
    10
```

|    |           BLKID | BORONAME   |   TotalPop |   WhitePop |   NonWhitePopulation |
|---:|----------------:|:-----------|-----------:|-----------:|---------------------:|
|  0 | 360050001001000 | The Bronx  |       8634 |       1242 |                 7392 |
|  1 | 360610238011009 | Manhattan  |       4970 |       2704 |                 2266 |
|  2 | 360810797012000 | Queens     |       4563 |        436 |                 4127 |
|  3 | 360610155006000 | Manhattan  |       4067 |       3507 |                  560 |
|  4 | 360471034001004 | Brooklyn   |       3918 |        605 |                 3313 |
|  5 | 360470325003001 | Brooklyn   |       3672 |         38 |                 3634 |
|  6 | 360050210014000 | The Bronx  |       3646 |        678 |                 2968 |
|  7 | 360470259021000 | Brooklyn   |       3419 |        531 |                 2888 |
|  8 | 360470343001000 | Brooklyn   |       3404 |        183 |                 3221 |
|  9 | 360610223021000 | Manhattan  |       3385 |        718 |                 2667 |

#### Classify the census blocks using a custom range interval using `CASE`

```sql
SELECT
    BLKID
    , BORONAME,
CASE
    WHEN POPN_TOTAL <= 10 THEN 'small'
    WHEN POPN_TOTAL > 10 AND POPN_TOTAL <= 200 THEN 'average'
    WHEN POPN_TOTAL > 200 THEN 'high'
END AS
    TYPE
FROM
    census_blocks
ORDER BY
    BORONAME DESC
LIMIT
    10
```

|    |           BLKID | BORONAME   | TYPE    |
|---:|----------------:|:-----------|:--------|
|  0 | 360050330003001 | The Bronx  | small   |
|  1 | 360050392001001 | The Bronx  | high    |
|  2 | 360050396001001 | The Bronx  | high    |
|  3 | 360050289001002 | The Bronx  | high    |
|  4 | 360050020001003 | The Bronx  | high    |
|  5 | 360050164001008 | The Bronx  | average |
|  6 | 360050160002000 | The Bronx  | average |
|  7 | 360050344002001 | The Bronx  | small   |
|  8 | 360050221013000 | The Bronx  | high    |
|  9 | 360050238003000 | The Bronx  | high    |

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

#### Count number of streets of each unique type (`DISTINCT` and `GROUP BY`)

```sql
SELECT
    DISTINCT(TYPE) AS STREET_TYPE
    , COUNT(*) AS COUNT
FROM streets
GROUP BY
    STREET_TYPE
ORDER BY
    COUNT
```

|    | STREET_TYPE                                             |   COUNT |
|---:|:-------------------------------------------------|--------:|
|  0 | motorway_link; residential                       |       1 |
|  1 | cycleway                                         |       2 |
|  2 | living_street                                    |       2 |
|  3 | primary; residential; motorway_link; residential |       2 |
|  4 | residential; motorway_link                       |       2 |
|  5 | undefined                                        |       2 |
|  6 | steps                                            |       7 |
|  7 | construction                                     |       8 |
|  8 | primary_link                                     |      12 |
|  9 | trunk                                            |      14 |
| 10 | trunk_link                                       |      15 |
| 11 | pedestrian                                       |      20 |
| 12 | service                                          |      90 |
| 13 | primary                                          |      98 |
| 14 | secondary                                        |     137 |
| 15 | motorway                                         |     227 |
| 16 | tertiary                                         |     257 |
| 17 | unclassified                                     |     337 |
| 18 | footway                                          |     345 |
| 19 | motorway_link                                    |     953 |
| 20 | residential                                      |   16560 |

### Spatial queries

#### Find duplicate points within a certain borough (`ST_X` and `ST_Y`)

```sql
SELECT
    st_x(T1.SHAPE) AS X
    , st_y(T1.SHAPE) AS Y
    , COUNT(*) AS COUNT
FROM
    Homicides T1
WHERE
    T1.BORONAME = 'Queens'
GROUP BY
    ST_X(T1.SHAPE), ST_Y(T1.SHAPE)
HAVING
    COUNT(*) > 1
```

|    |           X |            Y |   COUNT |
|---:|------------:|-------------:|--------:|
|  0 | 592796.9457 | 4512679.5541 |       2 |
|  1 | 595286.8248 | 4511502.8696 |       2 |
|  2 | 595719.1188 | 4509615.4108 |       2 |
|  3 | 596550.9795 | 4502936.1456 |       2 |
|  4 | 600693.1724 | 4504890.5882 |       2 |
|  5 | 600910.3951 | 4506349.8886 |       2 |
|  6 | 602224.2498 | 4505601.7733 |       2 |
|  7 | 602774.3020 | 4493937.5897 |       2 |
|  8 | 602825.2922 | 4494640.0928 |       2 |
|  9 | 602838.3109 | 4504421.8048 |       2 |
| 10 | 605123.2532 | 4503245.6874 |       2 |

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

#### Find all crime incidents located within a certain neighborhood (`ST_Within`)

```sql
SELECT *
FROM
    homicides
WHERE
    ST_Within(Shape, (SELECT shape FROM neighborhoods WHERE name = 'Springfield Gardens')) = 1
```

|    | INCIDENT_D          | BORONAME   |   NUM_VICTIM | PRIMARY_MO       |        ID | WEAPON   | LIGHT_DARK   |      YEAR | Shape                            |
|---:|:--------------------|:-----------|-------------:|:-----------------|----------:|:---------|:-------------|----------:|:---------------------------------|
|  0 | 2008/08/07 00:00:00 | Queens     |            1 |                  |  272.0000 |          | D            | 2008.0000 | POINT (604707.0115 4503808.7227) |
|  1 | 2003/05/17 00:00:00 | Queens     |            1 | GANG             |  610.0000 | gun      |              | 2003.0000 | POINT (604403.5032 4501833.0199) |
|  2 | 2003/12/20 00:00:00 | Queens     |            1 | ACCIDENTAL       |  951.0000 | gun      |              | 2003.0000 | POINT (604506.4653 4503601.6046) |
|  3 | 2004/02/14 00:00:00 | Queens     |            1 | ROBBERY/BURGLARY | 1031.0000 | knife    |              | 2004.0000 | POINT (603600.799 4503783.773)   |
|  4 | 2004/10/18 00:00:00 | Queens     |            1 | DRUGS            | 1393.0000 | gun      |              | 2004.0000 | POINT (603849.4094 4503625.6979) |
|  5 | 2004/11/12 00:00:00 | Queens     |            1 | ROBBERY/BURGLARY | 1438.0000 | gun      |              | 2004.0000 | POINT (604176.8612 4502059.4469) |
|  6 | 2004/12/02 00:00:00 | Queens     |            1 | REVENGE          | 1469.0000 | gun      |              | 2004.0000 | POINT (604554.7205 4503061.9049) |
|  7 | 2005/05/28 00:00:00 | Queens     |            1 | GANG             | 1690.0000 | gun      |              | 2005.0000 | POINT (605123.2532 4503245.6874) |
|  8 | 2005/08/21 00:00:00 | Queens     |            1 | REVENGE          | 1834.0000 | gun      |              | 2005.0000 | POINT (605123.2532 4503245.6874) |
|  9 | 2005/10/26 00:00:00 | Queens     |            1 | REVENGE          | 1939.0000 | gun      |              | 2005.0000 | POINT (604365.7047 4502874.717)  |
| 10 | 2006/12/02 00:00:00 | Queens     |            1 | DRUGS            | 2547.0000 | knife    | D            | 2006.0000 | POINT (603849.8359 4502149.0997) |
| 11 | 2007/05/26 00:00:00 | Queens     |            1 | DISPUTE          | 2768.0000 | gun      | L            | 2007.0000 | POINT (604495.4794 4501719.8418) |
| 12 | 2007/06/18 00:00:00 | Queens     |            1 | REVENGE          | 2806.0000 | gun      | D            | 2007.0000 | POINT (603780.4719 4502264.2333) |
| 13 | 2009/05/08 00:00:00 | Queens     |            1 |                  | 3396.0000 | gun      | L            | 2009.0000 | POINT (604510.3255 4502442.5821) |
| 14 | 2009/06/30 00:00:00 | Queens     |            1 |                  | 3521.0000 | gun      |              | 2009.0000 | POINT (604160.1474 4503157.554)  |
| 15 | 2009/07/20 00:00:00 | Queens     |            1 |                  | 3555.0000 | gun      | D            | 2009.0000 | POINT (604439.3402 4502652.6501) |
| 16 | 2010/05/15 00:00:00 | Queens     |            1 |                  | 3875.0000 | gun      |              | 2010.0000 | POINT (603980.3112 4501843.164)  |
| 17 | 2010/09/11 00:00:00 | Queens     |            1 |                  | 3951.0000 | gun      |              | 2010.0000 | POINT (603280.9473 4502731.6536) |

#### Find neighborhoods with the largest number of crimes commited (count number of homicides in each neighborhood) (`ST_Contains`)

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

#### Find what neighborhood(s) 10 most recent crime incidents are located within (`ST_Within`)

```sql
SELECT
    Points.INCIDENT_D
    , Points.BORONAME
    , Points.NUM_VICTIM
    , Points.PRIMARY_MO
    , Points.ID
    , Points.WEAPON
    , Points.LIGHT_DARK
    , Points.YEAR
    , Polys.Name AS NeighborhoodName
FROM
    Neighborhoods AS Polys
JOIN
    Homicides AS Points
ON
    ST_Within(Points.Shape, Polys.Shape) = 1
ORDER BY
    INCIDENT_D DESC
LIMIT 10
```

|    | INCIDENT_D          | BORONAME   |   NUM_VICTIM | PRIMARY_MO   |        ID | WEAPON   | LIGHT_DARK   |      YEAR | NeighborhoodName         |
|---:|:--------------------|:-----------|-------------:|:-------------|----------:|:---------|:-------------|----------:|:-------------------------|
|  0 | 2011/08/01 00:00:00 | The Bronx  |            1 |              | 4291.0000 | gun      |              | 2011.0000 | Mott Haven               |
|  1 | 2011/08/01 00:00:00 | Manhattan  |            1 |              | 4290.0000 | knife    |              | 2011.0000 | Yorkville                |
|  2 | 2011/07/30 00:00:00 | Queens     |            1 |              | 4287.0000 | gun      |              | 2011.0000 | Jamaica                  |
|  3 | 2011/07/29 00:00:00 | Brooklyn   |            1 |              | 4285.0000 | gun      |              | 2011.0000 | Williamsburg             |
|  4 | 2011/07/28 00:00:00 | The Bronx  |            1 |              | 4284.0000 | gun      |              | 2011.0000 | Wakefield-Williamsbridge |
|  5 | 2011/07/28 00:00:00 | Brooklyn   |            1 |              | 4283.0000 | gun      |              | 2011.0000 | Bushwick                 |
|  6 | 2011/07/26 00:00:00 | The Bronx  |            1 |              | 4282.0000 | gun      |              | 2011.0000 | Tremont                  |
|  7 | 2011/07/25 00:00:00 | Manhattan  |            1 |              | 4218.0000 | gun      |              | 2011.0000 | Washington Heights       |
|  8 | 2011/07/25 00:00:00 | The Bronx  |            1 |              | 4220.0000 | gun      |              | 2011.0000 | Tremont                  |
|  9 | 2011/07/25 00:00:00 | Brooklyn   |            1 |              | 4221.0000 | knife    |              | 2011.0000 | Bedford-Stuyvesant       |

#### Find duplicate points within a certain borough (`ST_Distance`) (slow to execute)

```sql
SELECT CAST(T1.ID AS integer) AS FirstPoint,
    CAST(T2.ID AS integer) SecondPoint,
    ST_Distance(T1.Shape, T2.Shape) Distance
FROM
    Homicides T1
JOIN
    Homicides T2
ON
    T1.ID < T2.ID
and
    ST_Distance(T1.Shape, T2.Shape) = 0
and
    T1.BORONAME = 'Queens'
ORDER BY
    Distance, FirstPoint
```

|    |   FirstPoint |   SecondPoint |   Distance |
|---:|-------------:|--------------:|-----------:|
|  0 |           41 |          2556 |     0.0000 |
|  1 |          454 |          1199 |     0.0000 |
|  2 |          667 |          1853 |     0.0000 |
|  3 |          783 |          1937 |     0.0000 |
|  4 |          907 |          1158 |     0.0000 |
|  5 |         1282 |          1544 |     0.0000 |
|  6 |         1690 |          1834 |     0.0000 |
|  7 |         1954 |          2016 |     0.0000 |
|  8 |         2264 |          2344 |     0.0000 |
|  9 |         2513 |          3350 |     0.0000 |
| 10 |         2664 |          3304 |     0.0000 |
| 11 |         3148 |          3448 |     0.0000 |

#### Find duplicate points within a certain borough (`ST_Equals`) (slow to execute)

```sql
SELECT CAST(T1.ID AS integer) AS FirstPointId,
    CAST(T2.ID AS integer) SecondPointId,
    ST_Distance(T1.Shape, T2.Shape) Distance
FROM
    Homicides T1
JOIN
    Homicides T2
ON
    T1.ID < T2.ID
and
    ST_Equals(T1.Shape, T2.Shape) = 1
and
    T1.BORONAME = 'Queens'
ORDER BY
    FirstPointId, SecondPointId
```

|    |   FirstPointId |   SecondPointId |   Distance |
|---:|---------------:|----------------:|-----------:|
|  0 |             41 |            2556 |     0.0000 |
|  1 |            454 |            1199 |     0.0000 |
|  2 |            667 |            1853 |     0.0000 |
|  3 |            783 |            1937 |     0.0000 |
|  4 |            907 |            1158 |     0.0000 |
|  5 |           1282 |            1544 |     0.0000 |
|  6 |           1690 |            1834 |     0.0000 |
|  7 |           1954 |            2016 |     0.0000 |
|  8 |           2264 |            2344 |     0.0000 |
|  9 |           2513 |            3350 |     0.0000 |
| 10 |           2664 |            3304 |     0.0000 |
| 11 |           3148 |            3448 |     0.0000 |

#### Find which subway stations have most crimes commited within the distance of 500 meters (slow to execute)

```sql
SELECT
    CAST(SUB.ID AS int) AS StationId,
    SUB.Name AS SubName
    , Count(*) AS CrimeCount
FROM
    homicides AS Crimes
JOIN
    SUBWAY_STATIONS AS SUB
ON
    ST_Distance(SUB.Shape, Crimes.Shape) < 500
GROUP BY
    SUB.ID, SUB.Name
ORDER BY
    CrimeCount DESC
LIMIT 5
```

|     |   StationId | SubName                   |   CrimeCount |
|----:|------------:|:--------------------------|-------------:|
|   1 |          85 | Sutter Ave                |           43 |
|   2 |         229 | Rockaway Ave              |           38 |
|   3 |         211 | Tremont Ave               |           37 |
|   4 |         212 | 182nd St                  |           37 |
|   5 |         209 | 170th St                  |           36 |
