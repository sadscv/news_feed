#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-11-8 下午8:20
# @Author  : sadscv
# @File    : test.py


def test():
    for i in range(10):
        print(i)

def gene():
    for i in range(3):
        yield i*i

a = test()
# print(a)