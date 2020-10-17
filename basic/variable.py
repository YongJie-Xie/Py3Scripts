#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author      : YongJie-Xie
@Contact     : fsswxyj@qq.com
@DateTime    : 0000-00-00 00:00
@Description : 多线程同步变量类，支持多线程同步、标记为全局变量等。
@FileName    : variable.py
@License     : MIT License
@ProjectName : Py3Scripts
@Software    : PyCharm
@Version     : 1.0
"""
from abc import ABCMeta, abstractmethod
from threading import Lock
from typing import Generic, Optional, TypeVar

T = TypeVar('T')


class SyncVariable(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, default: Optional[T] = None):
        self._variable = default
        self._variable_mutex = Lock()

    @property
    def variable(self) -> Optional[T]:
        with self._variable_mutex:
            return self._variable

    @variable.setter
    def variable(self, value: Optional[T]) -> None:
        with self._variable_mutex:
            self._variable = value

    # set alias name
    var = variable

    def __str__(self) -> str:
        return str(self.variable)

    def __repr__(self) -> str:
        return '<Sync {}(variable={})>'.format(self.__class__.__name__, self.variable)


class GlobalSyncVariable(SyncVariable, metaclass=ABCMeta):
    _instance = {}
    _instance_lock = Lock()

    def __new__(cls, *args, **kwargs):
        """利用内部锁实现的保证线程安全的单例设计模式，确保一个类只有一个实例存在"""
        _instance_key = (cls.__module__, cls.__name__)
        if _instance_key not in GlobalSyncVariable._instance:
            with GlobalSyncVariable._instance_lock:
                if _instance_key not in GlobalSyncVariable._instance:
                    GlobalSyncVariable._instance[_instance_key] = object.__new__(cls)
        return GlobalSyncVariable._instance[_instance_key]

    def __repr__(self) -> str:
        return '<GlobalSync {}(variable={})>'.format(self.__class__.__name__, self.variable)


__all__ = ['SyncVariable', 'GlobalSyncVariable']
