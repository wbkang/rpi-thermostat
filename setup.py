#!/usr/bin/env python3

from setuptools import setup, find_packages, Extension
import unittest


setup(
    name="rpithermostat",
    version='0.1.0',
    description='Home rpi thermostat',
    license='MIT',
    author='Woongbin Kang',
    author_email='wbk@outlook.com',
    packages=find_packages(exclude=['tests*']),
    setup_requires=['pytest-runner'],
    install_requires=["RPi.GPIO",
                      'pyowm',
                      'pytz',
                      'tzlocal',
                      'flask',
                      'alembic'],
    tests_require=['pytest'],
    include_package_data=True,
    entry_points={},
    classifiers=['Private :: Do not upload']
)
