"""Module for macprefs."""
from setuptools import find_packages, setup

setup(author='Andrew Udvare',
      author_email='audvare@gmail.com',
      description='Command and library to export macOS preferences.',
      entry_points={
          'console_scripts': [
              'prefs-export = macprefs.command:main',
              'macprefs-install-job = macprefs.command:install_job'
          ]
      },
      license='LICENSE.txt',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      name='macprefs',
      packages=find_packages(),
      python_requires='>=3.9',
      tests_require=['coveralls', 'nose', 'requests-mock'],
      url='https://github.com/Tatsh/macprefs',
      version='0.1.0')
