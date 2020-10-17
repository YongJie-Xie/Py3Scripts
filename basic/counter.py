#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author      : YongJie-Xie
@Contact     : fsswxyj@qq.com
@DateTime    : 0000-00-00 00:00
@Description : 多线程同步计数类，基于多线程同步变量类实现。
@FileName    : counter.py
@License     : MIT License
@ProjectName : Py3Scripts
@Software    : PyCharm
@Version     : 1.1
"""
from basic.variable import SyncVariable, GlobalSyncVariable


class Counter(SyncVariable):
    def __init__(self, default: int = 0):
        super().__init__(default)

    def increase(self, value: int = 1) -> None:
        with self._variable_mutex:
            self._variable += value


class GlobalCounter(GlobalSyncVariable):
    def __init__(self, default: int = 0):
        super().__init__(default)

    def increase(self, value: int = 1) -> None:
        with self._variable_mutex:
            self._variable += value


__all__ = ['Counter', 'GlobalCounter']
