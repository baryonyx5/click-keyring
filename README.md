# click-keyring

**click-keyring** provides a customized [click](https://click.palletsprojects.com) password option decorator to store and retrieve credentials using [keyring](https://keyring.readthedocs.io/en/latest/).

When a command is decorated with `click-keyring`:
* `click-keyring` generates a keyring service name using the command name by default (this can be customized).
* `click-keyring` uses the service name to look up an existing password using keyring.
* If an existing password is found, it is used as the param value.
* If not found, the user is prompted to enter a password.
* The new password is then saved to the keyring backend.

## Installation
```bash
pip install click-keyring
```

## Example
See the examples folder for additional examples.

```python
import click
from click_keyring import keyring_option


@keyring_option('-p', '--password')
@click.option('-u', '--username', prompt='Username')
@click.command()
def simple_cmd(username, password):
    """
    Example of click_keyring using defaults.

    The password will be saved to keyring with service name
    matching the click command name (in this case "simple_cmd").

    This can be overridden by setting `prefix` and/or `keyring_option`
     on the decorator.
    """
    click.echo()
    click.echo('** Command Params. User: {}, Password: {}'.format(username, password))


if __name__ == '__main__':
    simple_cmd()
```

When executed the first time, both username and password will be prompted.

```bash
~/g/c/examples python ./simple.py
Username: testuser
Password:

** Command Params. User: testuser, Password: testpw
~/g/c/examples
```

Subsequent executions using the same username will retrieve the password from the keyring backend.

```bash
~/g/c/examples python ./simple.py
Username: testuser

** Command Params. User: testuser, Password: testpw
~/g/c/examples
```

## Service Names
By default, the value of the `click.Command.name` attribute is used as the service name.  
The name is based on the function name or, if provided, the name argument on the `@click.command` decorator.

```python
@keyring_option('-p', '--password')
@click.option('-u', '--username', prompt='Username')
@click.command()
def simple_cmd(username, password):
    # service name will be the value of `simple_cmd.name`
    # This will likely be "simple-cmd" as click replaces underscores with hyphens.
    pass
```

A custom service name can be specified using the `prefix` argument.

```python
@keyring_option('-p', '--password', prefix='customnservice')
@click.option('-u', '--username', prompt='Username')
@click.command()
def simple_cmd(username, password):
    # service name will be "customnservice"
    pass
```

Other options on the command can be included in the service name using the `other_options` argument. 
This is an iterable of option names.  The values provided for those options is appended to the service name. 

```python
@keyring_option('-p', '--password', prefix='customnservice', other_options=('hostname',))
@click.option('-n', '--hostname')
@click.option('-u', '--username', prompt='Username')
@click.command()
def simple_cmd(username, hostname, password):
    # service name will be "customnservice_[value provided for hostname]"
    pass
```

