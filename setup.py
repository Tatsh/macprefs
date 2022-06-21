"""Module for macprefs."""
from setuptools import find_packages, setup

with open('README.md') as f:
    setup(author='Andrew Udvare',
          author_email='audvare@gmail.com',
          description='Command and library to export macOS preferences.',
          entry_points=dict(console_scripts=[
              'macprefs-install-job = macprefs.command:install_job',
              'prefs-export = macprefs.command:main',
          ], ),
          license='MIT',
          long_description=f.read(),
          long_description_content_type='text/markdown',
          name='macprefs',
          packages=find_packages(),
          python_requires='>=3.9',
          tests_require=['coveralls', 'nose', 'requests-mock'],
          url='https://github.com/Tatsh/macprefs',
          version='0.2.2')
