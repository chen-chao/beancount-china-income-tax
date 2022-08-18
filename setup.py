
# -*- coding: utf-8 -*-
from setuptools import setup

import codecs

with codecs.open('readme.md', encoding="utf-8") as fp:
    long_description = fp.read()
INSTALL_REQUIRES = [
    'beancount>=2.3.5',
]

setup_kwargs = {
    'name': 'beancount-china-income-tax',
    'version': '0.1.0',
    'description': 'A beancount plugin to calculate and validate china personal income tax',
    'long_description': long_description,
    'license': 'GPL-2.0',
    'author': '',
    'author_email': 'Chao Chen <wenbushi@gmail.com>',
    'maintainer': None,
    'maintainer_email': None,
    'url': '',
    'packages': [
        'beancount-china-income-tax',
    ],
    'package_data': {'': ['*']},
    'long_description_content_type': 'text/markdown',
    'install_requires': INSTALL_REQUIRES,
    'python_requires': '>=3.7',

}


setup(**setup_kwargs)
