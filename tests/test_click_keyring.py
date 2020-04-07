import os
import pytest
import click
import keyring
import click_keyring
from click.testing import CliRunner
from .conftest import KrTestBackEnd
from cryptography.fernet import Fernet


USER = 'testuser'
PW = 'testpw'


def fi(*args):
    """Format cli args and input"""
    return '\n'.join(a for a in args)


def fr(*args):
    """Format cli result output"""
    return 'CLI INPUT: {}'.format('|'.join(a for a in args))


@pytest.fixture(name='cli')
def cli_fixture(request):
    click_keyring_opts = {}
    if hasattr(request, 'param'):
        click_keyring_opts = request.param or {}

    @click_keyring.keyring_option('-p', '--password', **click_keyring_opts)
    @click.option('-o', '--other', default='other_default')
    @click.option('-u', '--username', prompt='Username')
    @click.command()
    def cli(username, password, other):
        click.echo(fr(username, password, other))

    return cli


def test_keyring():
    """Verify test keyring backend is selected and working"""
    assert isinstance(keyring.get_keyring(), KrTestBackEnd)
    system, user, pw = 'krtest', 'kruser', 'krpw'
    keyring.set_password(system, user, pw)
    assert keyring.get_password(system, user) == pw
    keyring.delete_password(system, user)


pw_save_params = [
    pytest.param(
        USER, PW, dict(args=['-u', USER, '-p', PW]), id='User, Pw provided as args'
    ),
    pytest.param(
        USER, PW, dict(args=['-u', USER], input=fi(PW)), id='User as arg, Pw at prompt'
    ),
    pytest.param(USER, PW, dict(input=fi(USER, PW)), id='User, Pw at prompt'),
]


@pytest.mark.parametrize('user, password, cli_input', pw_save_params)
def test_password_save(cli, user, password, cli_input):
    """
    Given a click command with valid arguments and prompt inputs and a
     an empty keyring store
    When the command is invoked
    Then the expected cli output is returned and password is saved
    """
    runner = CliRunner()
    result = runner.invoke(cli, **cli_input)
    assert fr(user, password) in result.output
    assert keyring.get_password(cli.name, user) == password


@pytest.fixture(name='populate_keyring')
def populate_keyring_fixture(cli):
    keyring.set_password(cli.name, USER, PW)
    assert keyring.get_password(cli.name, USER) == PW


pw_get_params = [
    pytest.param(USER, PW, dict(args=['-u', USER]), id='User provided as arg'),
    pytest.param(USER, PW, dict(input=fi(USER)), id='User at prompt'),
]


@pytest.mark.parametrize('user, password, cli_input', pw_get_params)
def test_password_get(populate_keyring, cli, user, password, cli_input):
    """
    Given a click command for a command and username already saved
    to the keyring store
    When the command is invoked
    Then the expected cli output is returned and password is retrieved
    from the keyring
    """
    runner = CliRunner()
    result = runner.invoke(cli, **cli_input)
    assert fr(user, password) in result.output
    assert keyring.get_password(cli.name, user) == password


prefix_params = [
    pytest.param(
        {'prefix': 'custom'},
        dict(args=['-u', USER, '-p', PW]),
        'custom',
        id='Service name set by prefix arg',
    ),
    pytest.param(
        {'other_options': 'other'},
        dict(args=['-u', USER, '-o', 'other_value', '-p', PW]),
        'cliother_value',
        id='Service name includes other_option',
    ),
]


@pytest.mark.parametrize('cli, cli_input, expected', prefix_params, indirect=['cli'])
def test_custom_prefix(cli, cli_input, expected):
    """
    Given a click command with a custom service prefix set for click_keyring
    When the command is invoked
    Then the expected cli output is returned and the password is saved
    to keying using the expected service name
    """
    runner = CliRunner()
    result = runner.invoke(cli, **cli_input)
    assert result.exit_code == 0
    assert keyring.get_password(expected, USER) == PW


@pytest.fixture(name='fernet_key')
def fernet_key_fixture():
    key = 'wu3pqWSLYQkDn0kkwUbtu0zhOCCvq4cd5Flm6rMYXIM='
    existing = os.environ.get('CLICK_KEYRING_KEY', None)
    os.environ['CLICK_KEYRING_KEY'] = key
    yield key
    if existing:
        os.environ['CLICK_KEYRING_KEY'] = existing


@pytest.mark.parametrize('cli', [{'encrypt': True}], indirect=['cli'])
def test_password_encrypt(fernet_key, cli):
    """
    Given a click command with a custom service prefix set for click_keyring
    When the command is invoked
    Then the expected cli output is returned and the password is saved
    to keying using the expected service name
    """
    runner = CliRunner()
    result = runner.invoke(cli, args=['-u', USER, '-p', PW])
    assert result.exit_code == 0
    enc_pw = keyring.get_password(cli.name, USER).encode()
    assert Fernet(fernet_key).decrypt(enc_pw).decode() == PW
