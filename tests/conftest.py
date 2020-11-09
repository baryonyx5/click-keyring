import pytest
import click
import keyring
import click_keyring
import keyring.backend
from collections import defaultdict


class KrTestBackEnd(keyring.backend.KeyringBackend):
    priority = 1

    def __init__(self, file):
        self.store = defaultdict(dict)

    def set_password(self, servicename, username, password):
        self.store[servicename][username] = password

    def get_password(self, servicename, username):
        try:
            return self.store[servicename][username]
        except Exception as ex:
            raise keyring.errors.KeyringError(ex)

    def delete_password(self, servicename, username):
        try:
            self.store[servicename].pop(username)
        except Exception as ex:
            raise keyring.errors.PasswordDeleteError(ex)


@pytest.fixture(name="kr", autouse=True)
def keyring_backend_fixture(tmpdir):
    file = tmpdir.join()
    keyring.set_keyring(KrTestBackEnd(file))
    assert isinstance(keyring.get_keyring(), KrTestBackEnd)


def format_input(*args):
    """Format cli args and input"""
    return "\n".join(a for a in args)


def format_result(*args):
    """Format cli result output"""
    return "CLI INPUT: {}".format("|".join(a for a in args))


def make_cli(keyring_opts=None, prompt_user=True):
    keyring_opts = keyring_opts or dict()
    user_opts = dict(prompt="Username") if prompt_user else dict()

    @click_keyring.keyring_option("-p", "--password", **keyring_opts)
    @click.option("-o", "--other", default="other_default")
    @click.option("-u", "--username", **user_opts)
    @click.command(name="cli")
    def cli(username, password, other):
        click.echo(format_result(username, password, other))

    return cli
