#!/usr/bin/env python

import os
import click
from click_keyring import keyring_option
from utils import echo_input, echo_result, echo_setup, cleanup, decrypt_result

os.environ.setdefault('CLICK_KEYRING_KEY', 'oDMORLJih9IucoQV5dW1qnhm2CMxz-qUnkFuFl2qACQ=')


@click.option('--clean-up', is_eager=True, callback=cleanup,
              is_flag=True, default=False,
              help='Remove keyring entries created by examples')
@keyring_option('-p', '--password', encrypt=True)
@click.option('-u', '--username', prompt='Username')
@click.command()
def encrypt_cmd(username, password, clean_up):
    """
    Example of click_keyring with encryption.

    Encrypting the password protects it from other applications that may access
    the os credential storage system.

    The password will be encrypted using fernet symmetric encryption
    (https://cryptography.io/en/latest/fernet/)

    You must set the `CLICK_KEYRING_KEY` environment variable to a valid encryption
    key.

    The same key used to save a credential must also be used to retrieve it later.
    """
    echo_setup(encrypt_cmd, encrypt_cmd.name, 'username')
    echo_input(username=username, password=password)
    echo_result(encrypt_cmd.name, username)
    decrypt_result(encrypt_cmd.name, username)


if __name__ == '__main__':
    encrypt_cmd()
