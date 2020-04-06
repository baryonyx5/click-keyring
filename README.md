# click-keyring

**click-keyring** provides a customized [click](https://click.palletsprojects.com) password option decorator to store and retrieve credentials using [keyring](https://keyring.readthedocs.io/en/latest/).

When a command is decorated with `click-keyring`:
* `click-keyring` uses the provided username (and optionally, other values) to generate a keyring service name.
* `click-keyring` uses the service name to look up an existing password using keyring.
* If an existing password is found, it is used as the param value.
* If not found, the user is prompted to enter a password.
* The new password is then saved to the keyring backend.

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

    The password will be saved to keyring with service name:

        `{prefix value}{username value}`

    The click command name (in this case "simple_cmd") is used as the prefix value by default.
    This can be overridden by setting `prefix="something"` on the `keyring_option` decorator.
    """
    pass


if __name__ == '__main__':
    simple_cmd()

```

