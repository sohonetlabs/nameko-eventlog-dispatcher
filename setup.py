# -*- coding: utf-8 -*-

import os
from codecs import open
from setuptools import setup, find_packages


file_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(file_path, 'README.rst'), 'r', 'utf-8') as readme_file:
    readme = readme_file.read()

setup(
    name='nameko-eventlog-dispatcher',
    version='0.4.2',
    description=(
        'Nameko dependency provider that dispatches log data using Events '
        '(Pub-Sub).'
    ),
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Julio Trigo',
    author_email='julio.trigo@sohonet.com',
    url='https://github.com/sohonetlabs/nameko-eventlog-dispatcher',
    packages=find_packages(exclude=['test', 'test.*']),
    python_requires='>=3.6',
    install_requires=['nameko>=2.6'],
    extras_require={
        'dev': [
            'pytest<=4.3.0',
            'flake8',
            'coverage',
            'restructuredtext-lint',
            'Pygments',
            'pytest-eventlet'
        ],
    },
    zip_safe=True,
    license='MIT License',
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
