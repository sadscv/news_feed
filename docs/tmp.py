#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-11-7 下午7:50
# @Author  : sadscv
# @File    : tmp.py


list = ''.join(input().split())
set = set(list)
max = -1
index = -1
for i in set:
    if list.count(i) > max:
        max = list.count(i)
        index = i
if max > len(list) / 3:
    print(index)
else:
    print(-1)




