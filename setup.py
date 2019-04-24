import re

from setuptools import setup, find_packages

with open('antibot/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)
    assert version is not None

setup(name='Antibot',
      version=version,
      author='Jean Giard',
      license='LGPL',
      classifier=[
          'Programming Language :: Python :: 3'
      ],
      entry_points={
          'console_scripts': ['antibot=antibot.main:run']
      },
      packages=find_packages(),
      install_requires=[
          'bottle',
          'pymongo',
          'requests',
          'pynject',
          'pyckson',
          'schedule',
          'slackclient',
          'straight.plugin',
          'jira'
      ],
      )
