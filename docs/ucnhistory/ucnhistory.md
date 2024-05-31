# ucnhistory

[Ucnhistory Index](../README.md#ucnhistory-index) / [Ucnhistory](./index.md#ucnhistory) / ucnhistory

> Auto-generated documentation for [ucnhistory.ucnhistory](../../ucnhistory/ucnhistory.py) module.

- [ucnhistory](#ucnhistory)
  - [ucnhistory](#ucnhistory-1)
    - [ucnhistory.get\_columns](#ucnhistoryget_columns)
    - [ucnhistory.get\_data](#ucnhistoryget_data)
    - [ucnhistory.get\_tables](#ucnhistoryget_tables)
    - [ucnhistory.to\_csv](#ucnhistoryto_csv)

## ucnhistory

[Show source in ucnhistory.py:12](../../ucnhistory/ucnhistory.py#L12)

Connect to database and fetch data from midas history tables based on
timestamps.

#### Attributes

- `df` *pd.DataFrame* - the data from the last fetch of the database
- `sql_config` *dict* - database connection settings
- `ssh_config` *dict* - ssh connection settings
- `table` *str* - table name from last fetch of the database

#### Examples

Fetch data from a known table and write to as csv for later use

```python
>>> from ucnhistory import ucnhistory
    m = ucnhistory()
    m.get_data('ucn2epicspressures_measured', start='March 4 12pm', stop='March 5')
    m.to_csv('mydata.csv')
```

Look for a table in the list of table and draw to figure

```python
>>> m = ucnhistory()
    tables = m.get_tables()
    for table in tables:
        if 'pressure' in table:
            data = m.get_data(table)
            data.plot()
            break
```

#### Signature

```python
class ucnhistory(object):
    def __init__(self): ...
```

### ucnhistory.get_columns

[Show source in ucnhistory.py:91](../../ucnhistory/ucnhistory.py#L91)

Get a list of the columns in a given table

#### Arguments

- `table` *str* - name of table for which to get the columns

#### Returns

- `list` - list of column names (str)

#### Signature

```python
def get_columns(self, table): ...
```

### ucnhistory.get_data

[Show source in ucnhistory.py:107](../../ucnhistory/ucnhistory.py#L107)

Get data form the data base.

#### Arguments

- `table` *str* - name of database table to fetch data from
- `columns` *list* - list of column names to fetch, if none fetch all
- `start` *str* - start time in any format, if none fetch past 24h
- `stop` *str* - end time in any format, if none fetch until now

#### Returns

pd.DataFrame

#### Signature

```python
def get_data(self, table, columns=None, start=None, stop=None): ...
```

### ucnhistory.get_tables

[Show source in ucnhistory.py:187](../../ucnhistory/ucnhistory.py#L187)

Get a list of all the tables in the database

#### Returns

- `list` - list of strings corresponding to available tables in the SQL
database

#### Signature

```python
def get_tables(self): ...
```

### ucnhistory.to_csv

[Show source in ucnhistory.py:208](../../ucnhistory/ucnhistory.py#L208)

Write dataframe to csv

#### Arguments

- `filename` *str* - name of file to write to

#### Signature

```python
def to_csv(self, filename): ...
```