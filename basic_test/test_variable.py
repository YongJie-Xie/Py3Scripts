#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author      : YongJie-Xie
@Contact     : fsswxyj@qq.com
@DateTime    : 0000-00-00 00:00
@Description : 多线程同步变量类的测试类
@FileName    : test_variable.py
@License     : MIT License
@ProjectName : Py3Scripts
@Software    : PyCharm
@Version     : 1.0
"""
import time
from threading import Thread

from basic import Logger, SyncVariable, GlobalSyncVariable

logger = Logger('test_variable', simplify=False)


def accumulate(target, number):
    for num in range(1, number + 1):
        target.variable += num
        logger.info('[%s] num: %s, now: %s', target.__class__.__name__, num, target)


@logger.warning('Testing SyncVariable Object.')
def test_sync_variable():
    class TestSyncVariable(SyncVariable):
        def __init__(self):
            super().__init__(0)

    thread_list = []
    for i in range(3):
        thread_list.append(Thread(target=accumulate, args=(TestSyncVariable(), 10)))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()


@logger.warning('Testing GlobalSyncVariable Object.')
def test_global_sync_variable():
    class TestGlobalSyncVariable(GlobalSyncVariable):
        def __init__(self):
            super().__init__(0)

    thread_list = []
    for i in range(3):
        thread_list.append(Thread(target=accumulate, args=(TestGlobalSyncVariable(), 10)))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()


def main():
    test_sync_variable()
    time.sleep(1)
    test_global_sync_variable()


if __name__ == '__main__':
    main()
