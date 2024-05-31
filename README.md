# ucnhistory

Fetch UCN history measurements from SQL database on `daq01.ucn.triumf.ca` as a pandas DataFrame. Allows for user-friendly timestamp input and write table to csv.

## Installation

Clone and install by the following

```bash
git clone https://github.com/ucn-triumf/ucnhistory.git
cd ucnhistory
pip install .
```

which will install the files on the user's python path. One can then import the package from anywhere on the device.

## Documentation and Examples

[See here](docs/ucnhistory/ucnhistory.md)

## Notes

### Database access

Note that access to the database requires the use of a password. This password should be stored in the python keyring in the following way:

```python
import keyring
keyring.set_password("ucn_history", "ucn_reader", password)
```

The password should be obtained from someone within the group.

### SSH access

Access to the DAQ computer is provided by mean of an SSH tunnel. One should copy their public key for password-less access to the machine.

```bash
ssh-copy-id ucn@daq01.ucn.triumf.ca
```