#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-11-21 下午2:20
# @Author  : sadscv
# @File    : test.py
import os

import pkg_resources

print(os.path.dirname(__file__))
print(pkg_resources.resource_filename('Data', ''))