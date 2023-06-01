# -*- coding: utf-8 -*-
from setuptools import setup

with open('readme.md', 'r', encoding="utf-8") as fp:
    long_description = fp.read()

setup_kwargs = {
    'name': 'beancount-china-income-tax',
    'version': '0.1.1',
    'description': 'A beancount plugin to calculate and validate china personal income tax',
    'long_description': long_description,
    'license': 'GPL-2.0',
    'author': 'Chao Chen',
    'author_email': 'Chao Chen <wenbushi@gmail.com>',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chen-chao/beancount-china-income-tax',
    'packages': [
        'beancount-china-income-tax',
    ],
    'package_data': {'': ['*']},
    'long_description_content_type': 'text/markdown',
    'install_requires': [
        'beancount>=2.3.5',
    ],
    'python_requires': '>=3.7',

}

setup(**setup_kwargs)