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


@keyring_option('-p', '--password', default='optiondefaultpw')
@click.option('-u', '--username', default='optiondefaultuser')
@cli.command()
def def1(username, password):
    """
    Example showing option default values.

    The defaults will be used if an option is not provided.
    """
    echo_setup(def1, def1.name, 'username', 'hostname')
    echo_input(username=username, password=password)
    echo_result(def1.name, username)


@keyring_option('-p', '--password')
@click.option('-u', '--username')
@cli.command()
def def2(username, password):
    """
    Example showing defaults from click context default map:

    https://click.palletsprojects.com/en/7.x/commands/#context-defaults

    The defaults will be used if an option is not provided.
    """
    echo_setup(def2, def2.name, 'username')
    echo_input(username=username, password=password)
    echo_result(def2.name, username)


if __name__ == '__main__':
    cli(default_map={
        "def2": {"username": "defaultmapuser", "password": "defaultmappw"}
    })
