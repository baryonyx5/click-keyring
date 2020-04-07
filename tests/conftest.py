import re
import pytest
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


@pytest.fixture(name='kr', autouse=True)
def keyring_backend_fixture(tmpdir):
    file = tmpdir.join()
    keyring.set_keyring(KrTestBackEnd(file))
    assert isinstance(keyring.get_keyring(), KrTestBackEnd)

