# ucnhistory

Fetch UCN history measurements from SQL database on `daq01.ucn.triumf.ca` as a pandas DataFrame. Allows for user-friendly timestamp input and write table to csv.

Quick Links:
* [Installation and Setup](#installation-and-setup)
* [Documentation and Examples](#documentation-and-examples)
    * [Reference](docs/ucnhistory/ucnhistory.md)
    * [Command line example](#command-line-usage)
    * [Python example](#python-example)

## Installation and Setup

Clone and install by the following

```bash
git clone https://github.com/ucn-triumf/ucnhistory.git
cd ucnhistory
pip install .
```

which will install the files on the user's python path. One can then import the package from anywhere on the device.

### Database access

Note that access to the database requires the use of a password. This password should be stored in the python keyring in the following way:

```python
import keyring
keyring.set_password("ucn_history", "ucn_reader", password)
```

The password should be obtained from someone within the group. Some issues with the keyring may exist for WSL usage. You may need to run the following before trying to set the password:

```bash
pip install keyrings.alt
```

### SSH access

Access to the DAQ computer is provided by mean of an SSH tunnel. First ensure that you have an ssh key present. If you run the command:
```bash
ls ~/.ssh
```
it should return a list of files, which should include something like `id_rsa` or `id_dsa` or similar. If file like this does not exist run the command
```
ssh-keygen
```
and follow the prompts (leave the password blank). Once you are certain you have an ssh public key you should copy it to daq01 for password-less access to the machine.

```bash
ssh-copy-id ucn@daq01.ucn.triumf.ca
```

## Documentation and Examples

### [See here for reference](docs/ucnhistory/index.md)

### Command line usage:

Help message:

```bash
usage: ucnhistory [-h] [-t TABLE] [-s START] [-e END] [-o OUTPUT] [-lt] [-lc] [-c COLUMN]

Fetch tables from ucn history SQL database to csv file

options:
  -h, --help            show this help message and exit
  -t TABLE, --table TABLE
                        Name of table from which to fetch
  -s START, --start START
                        Specify range start date and time
  -e END, --end END     Specify range end date and time
  -o OUTPUT, --output OUTPUT
                        Specify name of output csv file
  -lt, --list_tables    Display tables in database
  -lc, --list_columns   Display columns in database table (must specify table)
  -c COLUMN, --column COLUMN
                        Fetch column from table, use multiple times to get multiple columns. If
                        absent, fetch all columns
```

Some example usage:

```bash
# fetch an table from the past 24h nd save with default filename
ucnhistory -t ucn2epics_measured

# list all available tables
ucnhistory -lt

# list all columns in a table
ucnhistory -lc -t ucn2epics_measured

# get one table for a specified time period
ucnhistory -t ucn2epics_measured -s 'June 6 2024 12pm' -e 'June 6 2024 1pm'
```

### Python Example

The easiest thing is to use the [`search_data`](docs/ucnhistory/ucnhistory.md#ucnhistorysearch_data) function:

```python
from ucnhistory import ucnhistory

# initialize the object
h = ucnhistory()

# lets load some level probe data and a temperature
# command is case-insensitive

# default is to fetch past 24H
df = h.search_data(['TS112', 'lvl204', 'LvL203'])

# now lets fetch from a specific date range
# insensitive to specifics of the date and time formats
df = h.search_data(['TS112', 'lvl204', 'LvL203'],
                   start = 'Mar 5, 1pm 2025',
                   stop = '2025/03/05 14:00'
)
```



