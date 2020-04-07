#!/usr/bin/env python
import io
import re
from setuptools import setup, find_packages

_version_rgx = re.compile(r'__version__\s+=\s+"(.*)"')


with io.open("./click_keyring/__init__.py", "rt", encoding="utf8") as fh:
    version = _version_rgx.search(fh.read()).group(1)

setup(
    name='click-keyring',
    version=version,
    description='Save and retrieve passwords using Keyring with Click',
    author='Kris Seraphine',
    author_email='kris.seraphine@cdw.com',
    url='https://github.com/cdwlabs/click-keyring',
    classifiers=[
        'Environment :: Console',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(),
    install_requires=[
        'click',
        'cryptography',
        'keyring',
    ],
)
