#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author      : YongJie-Xie
@Contact     : fsswxyj@qq.com
@DateTime    : 0000-00-00 00:00
@Description : 多线程同步计数类的测试类
@FileName    : test_counter.py
@License     : MIT License
@ProjectName : Py3Scripts
@Software    : PyCharm
@Version     : 1.1
"""
import time
from threading import Thread

from basic import Logger, Counter, GlobalCounter

logger = Logger('test_counter', simplify=False)


def accumulate(target, number):
    for _ in range(number):
        target.increase()
        logger.info('[%s] now: %s', target.__class__.__name__, target)


@logger.warning('Testing Counter Object.')
def test_counter():
    thread_list = []
    for i in range(3):
        thread_list.append(Thread(target=accumulate, args=(Counter(0), 10)))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()


@logger.warning('Testing GlobalCounter Object.')
def test_global_counter():
    thread_list = []
    for i in range(3):
        thread_list.append(Thread(target=accumulate, args=(GlobalCounter(0), 10)))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()


def main():
    test_counter()
    time.sleep(1)
    test_global_counter()


if __name__ == '__main__':
    main()
