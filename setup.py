# -*- coding:utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='sol-static-analysis',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "click==8.1.3",
        "requests==2.28.1",
        "web3==5.31.1",
        "beautifulsoup4==4.11.1",
        "SQLAlchemy==1.4.44",
        "solc-select==1.0.2",
        "slither-analyzer==0.9.1"
    ],
    entry_points={
        "console_scripts": [
            "ssa=common.command:main",
        ]
    },
    url='',
    license='',
    author='embarek',
    author_email='hz9881838@gmail.com',
    description='solidity static analysis'
)
