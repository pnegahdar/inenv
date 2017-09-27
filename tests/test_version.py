#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of inenv.
# https://github.com/pnegahdar/inenv

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2015, Parham Negahdar <pnegahdar@gmail.com>

import pkg_resources
from inenv.version import __version__


def test_has_proper_version():
    assert __version__ == pkg_resources.get_distribution("inenv").version
