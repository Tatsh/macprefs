"""Module for macprefs."""
from setuptools import setup

setup(
    author='Andrew Udvare',
    author_email='audvare@gmail.com',
    description='Command and library to export macOS preferences.',
    entry_points={
        'console_scripts': [
            'prefs-export = macprefs.command:main',
        ]
    },
    install_requires=[],
    license='LICENSE.txt',
    long_description=open('README.md').read(),
    name='macprefs',
    packages=['macprefs'],
    tests_require=['coveralls', 'nose', 'requests-mock'],
    url='https://github.com/Tatsh/macprefs',
    version='0.0.1',
)
