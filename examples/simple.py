#!/usr/bin/env python

import click
from click_keyring import keyring_option
from utils import echo_input, echo_result, echo_setup, cleanup


@click.option('--clean-up', is_eager=True, callback=cleanup, is_flag=True,
              default=False, help='Remove keyring entries created by examples')
@keyring_option('-p', '--password')
@click.option('-u', '--username', prompt='Username')
@click.command()
def simple_cmd(username, password, clean_up):
    """
    Example of click_keyring using defaults.

    The password will be saved to keyring with service name
    matching the click command name (in this case "simple_cmd").

    This can be overridden by setting `prefix` and/or `keyring_option`
     on the decorator.
    """
    echo_setup(simple_cmd, simple_cmd.name, 'username')
    echo_input(username=username, password=password)
    echo_result(simple_cmd.name, username)


if __name__ == '__main__':
    simple_cmd()
