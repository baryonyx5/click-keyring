import os
import pytest
import click
import keyring
import click_keyring
from click.testing import CliRunner
from cryptography.fernet import Fernet
from .conftest import make_cli, KrTestBackEnd, format_input, format_result


USER = "testuser"
PW = "testpw"


def test_keyring():
    """Verify test keyring backend is selected and working"""
    assert isinstance(keyring.get_keyring(), KrTestBackEnd)
    system, user, pw = "krtest", "kruser", "krpw"
    keyring.set_password(system, user, pw)
    assert keyring.get_password(system, user) == pw
    keyring.delete_password(system, user)


def test_password_save():
    """
    Given a click command with valid arguments and prompt inputs and a
     an empty keyring store
    When the command is invoked
    Then the expected cli output is returned and password is saved
    """
    expecteduser = USER
    expectedpw = PW
    runner = CliRunner()
    cli = make_cli()
    result = runner.invoke(cli, args=["-u", USER, "-p", PW])
    assert format_result(expecteduser, expectedpw) in result.output
    assert keyring.get_password(cli.name, expecteduser) == expectedpw


@pytest.fixture(name="populate_keyring")
def populate_keyring_fixture():
    cli = make_cli()
    keyring.set_password(cli.name, USER, PW)
    assert keyring.get_password(cli.name, USER) == PW


def test_password_get(populate_keyring):
    """
    Given a click command for a command and username already saved
    to the keyring store
    When the command is invoked
    Then the expected cli output is returned and password is retrieved
    from the keyring
    """
    expecteduser = USER
    expectedpw = PW
    runner = CliRunner()
    cli = make_cli()
    result = runner.invoke(cli, args=["-u", USER])
    assert format_result(expecteduser, expectedpw) in result.output
    assert keyring.get_password(cli.name, expecteduser) == expectedpw


def test_keyring_using_option_as_prefix():
    """
    Given a click command with a click option name set for click_keyring prefix
    When the command is invoked
    Then the expected cli output is returned and the password is saved
    to keying using the expected service name
    """
    prefix = "cliother_value"
    runner = CliRunner()
    cli = make_cli({"other_options": ("other",)})

    result = runner.invoke(cli, args=["-u", USER, "-o", "other_value", "-p", PW])

    assert result.exit_code == 0
    assert keyring.get_password(prefix, USER) == PW


def test_keyring_using_custom_prefix():
    """
    Given a click command with a custom service prefix set for click_keyring
    When the command is invoked
    Then the expected cli output is returned and the password is saved
    to keying using the expected service name
    """
    prefix = "custom"
    runner = CliRunner()
    cli = make_cli({"prefix": prefix})

    result = runner.invoke(cli, args=["-u", USER, "-p", PW])
    assert result.exit_code == 0
    assert keyring.get_password(prefix, USER) == PW


@pytest.fixture(name="fernet_key")
def fernet_key_fixture():
    key = "wu3pqWSLYQkDn0kkwUbtu0zhOCCvq4cd5Flm6rMYXIM="
    existing = os.environ.get("CLICK_KEYRING_KEY", None)
    os.environ["CLICK_KEYRING_KEY"] = key
    yield key
    if existing:
        os.environ["CLICK_KEYRING_KEY"] = existing


def test_keyring_password_encrypt(fernet_key):
    """
    Given a click command with a custom service prefix set for click_keyring
    When the command is invoked
    Then the expected cli output is returned and the password is saved
    to keying using the expected service name
    """
    runner = CliRunner()
    cli = make_cli({"encrypt": True})
    result = runner.invoke(cli, args=["-u", USER, "-p", PW])
    assert result.exit_code == 0
    enc_pw = keyring.get_password(cli.name, USER).encode()
    assert Fernet(fernet_key).decrypt(enc_pw).decode() == PW
