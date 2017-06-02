#!/usr/bin/env python3

from setuptools import setup, find_packages, Extension
import unittest

dust_module = Extension('rpiweather.cdust',
                        libraries=['wiringPi'],
                        sources=['dust.c'])


setup(
    name="rpiweather",
    version='0.1.0',
    description='Home rpi weather station',
    license='MIT',
    author='Woongbin Kang',
    author_email='wbk@outlook.com',
    packages=find_packages(exclude=['tests*']),
    setup_requires=['pytest-runner'],
    install_requires=["RPi.GPIO",
                      'pyowm',
                      'pandas',
                      'pytz',
                      'tzlocal',
                      'alembic'],
    tests_require=['pytest'],
    include_package_data=True,
    entry_points={},
    ext_modules = [dust_module],
    classifiers=['Private :: Do not upload']
)
