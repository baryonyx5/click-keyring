import pytest
import keyring
from .conftest import make_cli, format_result, format_input
from click.testing import CliRunner


arguser = "arguser"
argpw = "argpassword"
defuser = "defaultuser"
defpw = "defaultpassword"
promptuser = "promptuser"
promptpw = "promptpassword"


def test_cli_user_as_arg_pw_as_arg_no_defaults():
    """
    Given a click_keyring cli function with no default values
    When passing the username and password as option arguments
    Then the command runs successfully with the expected output
    """
    expecteduser = arguser
    expectedpw = argpw
    runner = CliRunner()
    cli = make_cli()
    result = runner.invoke(cli, args=["-u", arguser, "-p", argpw])

    assert result.exit_code == 0
    assert format_result(expecteduser, expectedpw) in result.output
    assert keyring.get_password(cli.name, expecteduser) == expectedpw


def test_cli_user_as_arg_pw_at_prompt_no_defaults():
    """
    Given a click_keyring cli function with no default values
    When passing the username as option argument and entering password at prompt
    Then the command runs successfully with the expected output
    """
    expecteduser = "arguser"
    expectedpw = "promptpw"
    runner = CliRunner()
    cli = make_cli()

    result = runner.invoke(
        cli, args=["-u", expecteduser], input=format_input(expectedpw)
    )

    assert result.exit_code == 0
    assert format_result(expecteduser, expectedpw) in result.output
    assert keyring.get_password(cli.name, expecteduser) == expectedpw


def test_cli_user_at_prompt_pw_as_arg_no_defaults():
    """
    Given a click_keyring cli function with no default values
    When passing the expectedpw as an argument without a username
    Then the command fails and provides the expected error message
    """
    expecteduser = "promptuser"
    expectedpw = "argpw"
    err = 'Error: "username" option must be provided before the password'
    runner = CliRunner()
    cli = make_cli()

    result = runner.invoke(
        cli, args=["-p", expectedpw], input=format_input(expecteduser)
    )
    assert result.exit_code != 0
    assert err in result.output


def test_cli_user_at_prompt_pw_at_prompt_no_defaults():
    """
    Given a click_keyring cli function with no default values
    When entering the username and password when prompted
    Then the command runs successfully with the expected output
    """
    expecteduser = "promptuser"
    expectedpw = "promptpw"
    runner = CliRunner()
    cli = make_cli()

    result = runner.invoke(cli, args=[], input=format_input(expecteduser, expectedpw))

    assert result.exit_code == 0
    assert format_result(expecteduser, expectedpw) in result.output
    assert keyring.get_password(cli.name, expecteduser) == expectedpw


def test_cli_user_as_arg_pw_as_arg_with_defaults():
    """
    Given a click_keyring cli function with default values defined
    When passing the username and password as option arguments
    Then the command runs successfully with the argument values used
    """
    expecteduser = "arguser"
    expectedpw = "argpw"
    runner = CliRunner()
    cli = make_cli()

    result = runner.invoke(cli, args=["-u", expecteduser, "-p", expectedpw])

    assert result.exit_code == 0
    assert format_result(expecteduser, expectedpw) in result.output
    assert keyring.get_password(cli.name, expecteduser) == expectedpw


def test_cli_user_as_arg_pw_from_default():
    """
    Given a click_keyring cli function with default values defined
    When passing the username as option argument with password
    Then the command runs successfully with the default password used
    """
    expecteduser = arguser
    expectedpw = defpw
    runner = CliRunner()
    cli = make_cli()

    result = runner.invoke(
        cli, args=["-u", arguser], default_map={"username": defuser, "password": defpw}
    )

    assert result.exit_code == 0
    assert format_result(expecteduser, expectedpw) in result.output
    assert keyring.get_password(cli.name, expecteduser) == expectedpw


def test_cli_user_password_from_defaults():
    """
    Given a click_keyring cli function with default values defined
    When neither the username or password are provided as arguments
    Then the command runs successfully with the default values used
    """
    expecteduser = defuser
    expectedpw = defpw
    runner = CliRunner()
    cli = make_cli()

    result = runner.invoke(
        cli, args=[], default_map={"username": defuser, "password": defpw}
    )

    assert result.exit_code == 0
    assert format_result(expecteduser, expectedpw) in result.output
    assert keyring.get_password(cli.name, expecteduser) == expectedpw


def test_cli_user_from_default_pw_as_arg():
    """
    Given a click_keyring cli function with default values defined
    When passing the password as option argument without a username
    Then the command runs successfully with the default username used
    """
    expecteduser = defuser
    expectedpw = argpw
    runner = CliRunner()
    cli = make_cli(prompt_user=False)

    result = runner.invoke(
        cli, args=["-p", argpw], default_map={"username": defuser, "password": defpw}
    )
    assert result.exit_code == 0
    assert format_result(expecteduser, expectedpw) in result.output
    assert keyring.get_password(cli.name, expecteduser) == expectedpw
