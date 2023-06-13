#!/usr/bin/env python
from distutils.core import setup, find_packages


setup(
    name="boa_learn",
    version="0.1",
    description="A library for working with biomarkers of aging data",
    author="Seth Paulson",
    author_email="sarudak@gmail.com",
    package_data={
        'boa_learn': ['data/*'],  # All CSV files in the data subdirectory of your_package
    },
    packages=["boa_learn"],
)
