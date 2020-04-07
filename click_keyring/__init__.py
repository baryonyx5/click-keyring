import os
import re
import click
import keyring
from cryptography.fernet import Fernet

__version__ = "0.1.0"


service_name_rgx = re.compile(r'[\s.\-_]')


def create_service_name(*options):
    """
    Build service name by concatenating provided arguments.

    The default OSX and Windows backends have no problem with
    spaces, hyphens or periods but these are removed in case
    a custom backend does not like them

    Args:
        options: One or more strings to combine into the service name

    Returns:
        name (str): Combined string
    """
    return ''.join(str(o) for o in options)


def keyring_option(
    *param_decls,
    prefix=None,
    user_option='username',
    other_options=None,
    encrypt=False,
    **attrs,
):
    """
    Click option decorator for passwords stored in keyring.

    This option will do the following:
    - If a password value is provided, save it to keyring store.
    - If not provided, check the keyring store for a previously saved password.
    - If not provided and not found in keyring store, prompt for the password and then save it.
    
    The keyring service name a concatenation of prefix, user_option value and other_options values. 
    This allows an app to save different passwords based on value combinations. 

    By default, a "username" option is assumed and password is saved for each unique username value
    provided. To save passwords for each unique hostname/username combination, set the "other_options"
    argument to "('hostname',)". This assumes there is a "hostname" option defined.   


    Args:
        param_decls (str): short and/or long decls ex: ("-p", "--password")
        prefix (str): makes up first part of keyring service name where password is stored.
        user_option (None, str): Identifies the click option name that holds the username.
         If not provided, defaults to "username"
        other_options (None, tuple): Additional click option names to use as part of 
         the keyring service name.
        encrypt (bool): Encrypt the password in the keyring if True
         attrs (dict): Addition keyword arguments to pass to click option

    """
    other_options = other_options or ()
    # Ensure other_options is an iterable of strings
    if isinstance(other_options, str):
        other_options = (other_options,)
    cls = EncKeyRing if encrypt else KeyRing

    def decorator(f):
        attrs['prompt'] = False
        attrs['hide_input'] = True
        attrs.setdefault('confirmation_prompt', False)
        attrs['callback'] = cls(prefix, user_option, other_options)
        return click.option(*(param_decls or ('--password',)), **attrs)(f)

    return decorator


class KeyRing:
    def __init__(self, prefix=None, username_option='username', other_options=None):
        self.prefix = prefix
        self.user_option = username_option
        self.other_options = other_options or ()

    def service(self, ctx):
        """Return keyring service name."""
        prefix = self.prefix or ctx.command.name
        others = [self._get_option_values(ctx, o) for o in self.other_options]
        svc = create_service_name(prefix, *others)
        return svc

    def username(self, ctx):
        return self._get_option_values(ctx, self.user_option)

    @staticmethod
    def _get_option_values(ctx, option):
        try:
            return ctx.params[option]
        except KeyError:
            if option not in [p.name for p in ctx.command.params]:
                msg = 'Option "{}" does not exist on command "{}"'.format(
                    option, ctx.command.name
                )
            else:
                msg = '"{}" option must be provided before the password'.format(option)
            raise click.exceptions.BadOptionUsage('password', msg, ctx)

    @staticmethod
    def _get_service(options):
        return '_'.join(str(o) for o in options)

    def get(self, ctx):
        """Get a password saved previously for the provided hostname and username."""
        try:
            return keyring.get_password(self.service(ctx), self.username(ctx))
        except keyring.errors.KeyringError:
            return None

    def save(self, service, username, password):
        """Save a keyring credential for the provided hostname and username."""
        keyring.set_password(service, username, password)

    def __call__(self, ctx, _, value):
        if not value:
            value = self.get(ctx)
        if not value:
            value = click.prompt('Password', hide_input=True, type=str)

        self.save(self.service(ctx), self.username(ctx), value)
        return value


class EncKeyRing(KeyRing):
    key = None

    def __init__(self, prefix, username_option, other_options=None):
        super().__init__(prefix, username_option, other_options)
        self.fernet = self._init_f()

    def get(self, ctx):
        pw = super().get(ctx)
        if pw:
            return self.decrypt(pw)

    def save(self, service, username, password):
        """Save a keyring credential for the provided hostname and username."""
        keyring.set_password(service, username, self.encrypt(password))

    def decrypt(self, pw):
        return self.fernet.decrypt(pw.encode()).decode()

    def encrypt(self, pw):
        return self.fernet.encrypt(pw.encode()).decode()

    def _init_f(self):
        err = 'No encrypt key found. Set ClickKeyRing.key ' \
              'class attribute or "CLICK_KEYRING_KEY" envvar'
        key = self.key or os.environ.get('CLICK_KEYRING_KEY')
        if not key:
            click.exceptions.ClickException(err)
        return Fernet(key)
