from .ucnhistory import ucnhistory
from .search import search
from argparse import ArgumentParser
import os
import datetime

def main():
    # setup argument parser
    parser = ArgumentParser(prog = 'ucnhistory',
                            description='Fetch tables from ucn history SQL database to csv file')

    parser.add_argument('-t', '--table',
                        help='Name of table from which to fetch',
                        default=None,
                        required=False,
                        action='store')
    parser.add_argument('-s', '--start',
                        help='Specify range start date and time',
                        required=False,
                        default=None,
                        action='store')
    parser.add_argument('-e', '--end',
                        help='Specify range end date and time',
                        required=False,
                        default=None,
                        action='store')
    parser.add_argument('-o', '--output',
                        help='Specify name of output csv file',
                        required=False,
                        default=None,
                        action='store')
    parser.add_argument('-lt', '--list_tables',
                        help='Display tables in database',
                        required=False,
                        action='store_true')
    parser.add_argument('-lc', '--list_columns',
                        help='Display columns in database table (must specify table)',
                        required=False,
                        action='store_true')
    parser.add_argument('-c', '--column',
                        help='Fetch column from table, use multiple times to get multiple columns. If absent, fetch all columns',
                        required=False,
                        action='append')

    # parse input arguments
    args = parser.parse_args()

    # setup fetch history
    uhist = ucnhistory()

    # run
    if args.list_tables:
        tables = uhist.get_tables()
        print('\n'.join(tables))

    elif args.list_columns:

        if args.table is None:
            print("Must define a table name")
        else:
            columns = uhist.get_columns(args.table)
            print('\n'.join(columns))

    elif args.table is None:
        print("Must define a table name")

    else:
        uhist.get_data(args.table,
                        columns=args.column,
                        start=args.start,
                        stop=args.end)

        # get default output filename
        filename = args.output
        if filename is not None:
            filaname = os.path.splitext(filename)[0] + '.csv'
        else:
            time = datetime.datetime.now()
            time = time.strftime("%y%m%d")
            filename = f'{time}_{args.table}.csv'

        uhist.to_csv(filename)
