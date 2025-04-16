# Get MIDAS history from SQL table

from getpass import getpass
import pymysql
from datetime import datetime, timedelta
from dateutil.parser import parse as dparse
import pandas as pd
import keyring
from sshtunnel import SSHTunnelForwarder
import time
import ucnhistory as uhist
import numpy as np

class ucnhistory(object):
    """Connect to database and fetch data from midas history tables based on
    timestamps.

    Attributes:
        df (pd.DataFrame): the data from the last fetch of the database
        sql_config (dict): database connection settings
        ssh_config (dict): ssh connection settings
        table (str): table name from last fetch of the database

    Example:
        Fetch data from a known table and write to as csv for later use
        >>> from ucnhistory import ucnhistory
            m = ucnhistory()
            m.get_data('ucn2epicspressures_measured', start='March 4 12pm', stop='March 5')
            m.to_csv('mydata.csv')

        Look for a table in the list of table and draw to figure
        >>> m = ucnhistory()
            tables = m.get_tables()
            for table in tables:
                if 'pressure' in table:
                    data = m.get_data(table)
                    data.plot()
                    break
    """

    sql_config = {'host': 'localhost',
                  'port': 3306,
                  'user': 'ucn_reader',
                  'database': 'ucn_history',
                 }

    ssh_config = {'host': 'daq01.ucn.triumf.ca',
                  'port': 22,
                  'user': 'ucn'
                 }

    def __init__(self):

        try:
            self._tunnel = SSHTunnelForwarder((self.ssh_config['host'], self.ssh_config['port']),
                                    ssh_username = self.ssh_config['user'],
                                    remote_bind_address=(self.sql_config['host'],
                                                         self.sql_config['port']))
        except (ValueError, pymysql.err.OperationalError):
            password = getpass(f'{self.ssh_config["user"]}@{self.ssh_config["host"]} password: ')
            self._tunnel = SSHTunnelForwarder((self.ssh_config['host'], self.ssh_config['port']),
                                    ssh_username = self.ssh_config['user'],
                                    remote_bind_address=(self.sql_config['host'],
                                                         self.sql_config['port']),
                                    ssh_password=password)

    def _date_parser(self, date=None):
        # Convert human-readable dates to datetime
        # date (str): date input from user

        if date is not None:
            dt = dparse(date)
        else:
            dt = datetime.now()

        return dt

    def _connect(self):

        # database password
        password = keyring.get_password(self.sql_config['database'],
                                        self.sql_config['user'])

        # set password
        if password == '':
            password = getpass('No password found in keyring. ' +\
                               f'SQL password for user {self.sql_config["user"]}'+\
                               f' and database {self.sql_config["database"]}: ')

        self._tunnel.start()
        self._connector = pymysql.connect(password=password,
                                    host = self.sql_config['host'],
                                    user = self.sql_config['user'],
                                    database = self.sql_config['database'],
                                    port = self._tunnel.local_bind_port,
                                    )

    def _disconnect(self):
        self._connector.close()
        self._tunnel.stop()

    def get_columns(self, table, _reconnect=True):
        """Get a list of the columns in a given table

        Args:
            table (str): name of table for which to get the columns
            _reconnect (bool): if true connect to server then disconnect at end

        Returns:
            list: list of column names (str)
        """

        database = self.sql_config['database']

        if _reconnect:
            self._connect()
        cur = self._connector.cursor()
        cur.execute(f"SHOW COLUMNS FROM {database}.{table}")

        if _reconnect:
            self._disconnect()

        return [c[0] for c in cur.fetchall()]

    def get_data(self, table, columns=None, start=None, stop=None):
        """Get data form the data base.

        Args:
            table (str): name of database table to fetch data from
            columns (list): list of column names to fetch, if none fetch all
            start (str): start time in any format, if none fetch past 24h
            stop (str): end time in any format, if none fetch until now

        Returns:
            pd.DataFrame
        """

        self.table = table

        # check inputs
        if type(columns) is str:
            columns = [columns]

        # convert input to datetime
        if isinstance(start, datetime.datetime): date1 = start
        else:                                    date1 = self._date_parser(start)

        if isinstance(stop, datetime.datetime):  date2 = stop
        else:                                    date2 = self._date_parser(stop)

        # get epoch times
        epoch1 = int(date1.timestamp())
        epoch2 = int(date2.timestamp())

        # check same date input: get 24h of data
        if epoch1 == epoch2:
            epoch1 -= 24 * 3600
            date1 -= timedelta(hours=24)

        # get history -----------------------
        database = self.sql_config['database']

        # get column names
        if columns is None:
            columns = self.get_columns(table)

        if '_i_time' not in columns:
            columns.append('_i_time')

        # get cursor
        self._connect()

        # get data
        cols = ', '.join(columns)
        df = pd.read_sql_query(f'SELECT {cols} from {database}.{table} WHERE '+\
                f"_i_time >= {epoch1} and _i_time < {epoch2}", self._connector)
        self._disconnect()

        # check data
        if len(df) == 0:
            raise IOError(f'No data found in {database}.{table}')

        # rename columns
        df.rename(columns={'_i_time': 'epoch_time'}, inplace=True)

        # drop fully empty columns
        df.dropna(inplace=True, how='all', axis='columns')

        # drop time columns
        df.drop(columns=[c for c in df.columns if c in ['_t_time', '_i_time']], inplace=True)

        # to datetime
        df['time'] = pd.to_datetime(df['epoch_time'], unit='s')

        # account for timezone
        df.set_index('time', inplace=True)
        df = df.tz_localize('UTC').tz_convert('America/Vancouver')

        self.df = df

        return df

    def get_tables(self):
        """Get a list of all the tables in the database

        Returns:
            list: list of strings corresponding to available tables in the SQL
            database
        """

        # _connect
        self._connect()

        # get tables
        cur1 = self._connector.cursor()
        cur1.execute(f'SHOW TABLES FROM {self.sql_config["database"]};')
        tables = [t[0] for t in cur1.fetchall()]

        # _connect
        self._disconnect()

        return sorted(tables)

    def search_data(self, name, start=None, stop=None, rename_column=True):
        """Search for table and column name and get the data right away.

        Args:
            name (str): name of the quantity
            start (str): start time in any format, if none fetch past 24h
            stop (str): end time in any format, if none fetch until now

        Returns:
            pd.DataFrame: data fetched
        """

        # search with lists
        if isinstance(name, (list, tuple, np.ndarray)):
            dflist = [self.search_data(n, start, stop, rename_column) for n in name]
            df = pd.concat(dflist, axis='columns')
            df.drop(columns='epoch_time', inplace=True)
            return df

        # apply search
        path = uhist.search(name)

        # if multitable, look for the one that works
        data = None
        if type(path) is list:
            for p in path:
                try:
                    data = self.get_data(**p, start=start, stop=stop)
                except OSError as err:
                    pass
                else:
                    path = p
                    break

        # if not then just try to fetch
        else:
            data = self.get_data(**path, start=start, stop=stop)

        # check that data is found
        if data is None:
            raise RuntimeError(f'Good data not found! Paths: {path}')

        # rename the column
        if rename_column:
            data = data.rename(columns={path['columns'][0]:name})

        return data

    def to_csv(self, filename):
        """Write dataframe to csv

        Args:
            filename (str): name of file to write to
        """

        # write header
        header = (  f'# Contents of database {self.sql_config["database"]}.{self.table}',
                    f'# Host: {self.sql_config["host"]}',
                    f'# {datetime.now()}',
                    '# \n'
                )

        with open(filename, 'w') as fid:
            fid.write('\n'.join(header))

        # write file contents
        self.df.to_csv(filename, mode='a')
