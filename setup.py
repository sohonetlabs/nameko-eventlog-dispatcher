# -*- coding: utf-8 -*-

import os
from codecs import open
from setuptools import setup, find_packages


file_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(file_path, 'README.rst'), 'r', 'utf-8') as readme_file:
    readme = readme_file.read()

setup(
    name='nameko-eventlog-dispatcher',
    version='0.1.0',
    description=(
        'Nameko dependency provider that dispatches log data using Events '
        '(Pub-Sub).'
    ),
    long_description=readme,
    author='Julio Trigo',
    author_email='julio.trigo@sohonet.com',
    url='https://github.com/sohonetlabs/nameko-eventlog-dispatcher',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=['nameko>=2.5.4'],
    extras_require={
        'dev': [
            'pytest==3.1.2',
            'flake8==3.3.0',
            'coverage==4.4.1',
        ],
    },
    zip_safe=True,
    license='MIT License',
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ]
)
