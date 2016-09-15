# coding=utf-8

# Shane - a poor man and/or hipster's TUI screenwriting software
# Copyright (C) 2016 Tobias Heukäufer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup

with open("README.rst") as f:
    long_description = f.read()

setup(
    name="Shane",

    version="1.0b1",

    license="GNU General Public License v3.0",

    description="A poor man and/or hipster\'s screenwriting software.",
    long_description=long_description,
    keywords="screenplay screenwriting movie film tv",

    url="https://github.com/Tobchen/Shane",

    author="Tobias Heukäufer",
    author_email="tobi@tobchen.de",

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",

        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",

        "Environment :: Console :: Curses",

        "Topic :: Text Editors",
        "Intended Audience :: End Users/Desktop",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],

    packages=["shane", "shane.io"],

    # install_requires=[],

    entry_points={
        "console_scripts": [
            "shane=shane.main:run",
        ],
    },
)
