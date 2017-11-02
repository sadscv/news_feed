# coding=utf-8

import difflib

#使用difflib比对新旧页面源码，发现增加的部分，提取url和text
def diff_file(lines1, lines2):
    if (not lines1) or (not lines2):
        return
    diff_text = ''
    #difflib.ndiff()按行进行比较，然后输出一个差别报告
    diff = list(difflib.ndiff(lines1.splitlines(), lines2.splitlines()))
    for i in diff:
        if i.startswith('+'):
            diff_text += i[1:]
    return diff_text





