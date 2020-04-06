#!/usr/bin/env python

import click
from click_keyring import keyring_option
from utils import echo_input, echo_result, echo_setup, cleanup


@click.option('--clean-up', is_eager=True, callback=cleanup, is_flag=True,
              default=False, help='Remove keyring entries created by examples')
@click.group()
def cli(clean_up):
    """
    Examples showing `click_keyring` for a click app with command groups.
    """
    pass


@keyring_option('-p', '--password', prefix='example', other_options=('hostname',))
@click.option('-n', '--hostname', default='server.xyz.com')
@click.option('-u', '--username', prompt='User Name')
@cli.command()
def cmd1(hostname, username, password):
    """
    Example using custom options for the keyring service name.

    The password will be saved to keyring with service name:

        `{prefix value}{username value}{hostname value}`

    Setting a custom prefix allows credentials stored by this command to be used by other commands
    with the same prefix, user_option and other_options values
    """
    echo_setup(cmd1, 'example', 'username', 'hostname')
    echo_input(username=username, hostname=hostname, password=password)
    echo_result('example', username, hostname)


@keyring_option('-p', '--password', prefix='example', user_option='userid', other_options=('hostname',))
@click.option('-n', '--hostname', default='server.xyz.com')
@click.option('-u', '--userid', prompt='User ID')
@cli.command()
def cmd2(hostname, userid, password):
    """
    Example using custom username option.

    The password will be saved to keyring with service name:

        `{prefix value}{userid value}{hostname value}`

    The user option must be set explicitly to "userid" because it differs from the default "username"

    Since cmd1 and cmd1 have the same service name format (same prefix value and other_options), the same
    keyring entries will be used for both.

    """
    echo_setup(cmd2, 'example', 'userid', 'hostname')
    echo_input(userid=userid, hostname=hostname, password=password)
    echo_result('example', userid, hostname)


if __name__ == '__main__':
    cli()
