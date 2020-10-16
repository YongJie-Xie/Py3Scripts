#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author      : YongJie-Xie
@Contact     : fsswxyj@qq.com
@DateTime    : 0000-00-00 00:00
@Description : 计数器类，支持利用同步锁对数值进行顺序变更。
@FileName    : counter.py
@License     : MIT License
@ProjectName : MyScripts
@Software    : PyCharm
@Version     : 1.0
"""


class Counter:
    def __init__(self, default: int = 0, is_process: bool = False):
        if is_process:
            from multiprocessing import Lock
        else:
            from threading import Lock
        self._count = default
        self._count_mutex = Lock()

    @property
    def count(self) -> int:
        with self._count_mutex:
            return self._count

    @count.setter
    def count(self, value: int) -> None:
        with self._count_mutex:
            self._count = value

    def add(self, value: int = 1) -> None:
        with self._count_mutex:
            self._count += value

    def __str__(self):
        return str(self.count)

    def __repr__(self):
        return '<Counter(count={count})>'.format(count=self.count)


__all__ = ['Counter']
