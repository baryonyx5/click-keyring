import os
import click
import keyring
import inspect
from click_keyring import create_service_name
from cryptography.fernet import Fernet

activity_file = 'example_services_to_cleanup.txt'


def cleanup(ctx, param, value):
    """
    Remove entries in the keyring backend created by the examples.
    """
    if not value:
        return
    with open(activity_file) as fh:
        services_to_remove = set(fh.readlines())
    for entry in services_to_remove:
        service, username = [e.strip() for e in entry.split(',')]
        svc_text = 'service: "{}", username: "{}"'.format(service, username)
        try:
            keyring.delete_password(service, username)
            click.echo('Removed keyring entry {}'.format(svc_text))
        except keyring.errors.PasswordDeleteError:
            click.echo('Keyring entry for {} not found'.format(svc_text))

    os.unlink(activity_file)
    ctx.exit()


def echo_setup(f, prefix, user_option, *other_options):
    w = 120
    click.echo()
    click.echo(f' click_keyring example command "{f.name}" '.center(w, '='))
    click.echo()
    click.echo(inspect.cleandoc(f.__doc__))
    click.echo()
    click.echo('='.center(w, '='))
    click.echo()
    click.echo('click_keyring Settings:')
    click.echo(' - Service Prefix: "{}"'.format(prefix))
    click.echo(' - Service Username Option: "{}"'.format(user_option))
    click.echo(
        ' - Other Service Options: {}'.format(
            ','.join('"{}"'.format(o) for o in other_options)
        )
    )
    click.echo('')


def echo_input(**kwargs):
    inputs = '\n'.join([' - {}: "{}"'.format(k, v) for k, v in kwargs.items()])
    click.echo('Command Input:\n{}\n'.format(inputs))


def echo_result(prefix, username, *options):
    service = create_service_name(prefix, username, *options)
    backend = keyring.get_keyring().name
    value = keyring.get_password(service, username)
    click.echo(
        'Keyring Results\n - Backend: "{}"\n - Service: "{}"\n - Value: "{}"'.format(
            backend, service, value
        )
    )
    with open(activity_file, 'a') as fh:
        fh.write('{},{}\n'.format(service, username))


def decrypt_result(prefix, username, *options):
    service = create_service_name(prefix, username, *options)
    f = Fernet(os.environ['CLICK_KEYRING_KEY'])
    val = f.decrypt(keyring.get_password(service, username).encode())
    click.echo(' - Decrypted: "{}"'.format(val.decode()))
