# Search tables for column names
# Derek Fujimoto
# Oct 2024
from tqdm import tqdm
import ucnhistory

hist = ucnhistory.ucnhistory()

names = {}

def build_tables():
    global names
    tables = hist.get_tables()
    hist._connect()
    for table in tqdm(tables, desc='Building key names dictionary', leave=True):
        if 'measured' in table:
            names[table] = hist.get_columns(table, _reconnect=False)
    hist._disconnect()

# search function
def search(var):
    """Use the get tables and get columns feature to search for matching names"""

    global names

    if len(names) == 0:
        build_tables()

    # to lower and no special characters
    v = var.lower()
    v = v.replace(' ', '_')
    v = v.replace(':', '_')

    # look for all possible key matches
    found_key = []
    for table, columns in names.items():
        for col in columns:
            if v in col:
                found_key.append({'table':table, 'columns':[col]})

    # return depending on state
    if len(found_key) == 1:
        return found_key[0]
    elif len(found_key) == 0:
        raise RuntimeError(f'No columns found for variable {var}')
    else:
        return found_key
