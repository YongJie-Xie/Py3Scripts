#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author      : YongJie-Xie
@Contact     : fsswxyj@qq.com
@DateTime    : 0000-00-00 00:00
@Description : 日志操作类，支持控制台输出着色、文件输出、装饰器调用等。
@FileName    : logger.py
@License     : MIT License
@ProjectName : Py3Scripts
@Software    : PyCharm
@Version     : 1.2
"""
import logging
import os
import sys
import time
import traceback
from functools import wraps, partial
from inspect import isfunction
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, WARN, FATAL
from logging.handlers import RotatingFileHandler
from threading import Lock
from typing import Union, Optional

if sys.version_info < (3, 8):
    import io


    class LoggerClass(logging.Logger):
        _srcfile = os.path.normcase(logging.addLevelName.__code__.co_filename)

        def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1) -> None:
            sinfo = None
            if self._srcfile:
                try:
                    fn, lno, func, sinfo = self.findCaller(stack_info, stacklevel)
                except ValueError:
                    fn, lno, func = "(unknown file)", 0, "(unknown function)"
            else:
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
            if exc_info:
                if isinstance(exc_info, BaseException):
                    exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
                elif not isinstance(exc_info, tuple):
                    exc_info = sys.exc_info()
            record = self.makeRecord(self.name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)
            self.handle(record)

        def findCaller(self, stack_info=False, stacklevel=1):
            f = logging.currentframe()
            if f is not None:
                f = f.f_back
            orig_f = f
            while f and stacklevel > 1:
                f = f.f_back
                stacklevel -= 1
            if not f:
                f = orig_f
            rv = "(unknown file)", 0, "(unknown function)", None
            while hasattr(f, "f_code"):
                co = f.f_code
                filename = os.path.normcase(co.co_filename)
                if filename == self._srcfile:
                    f = f.f_back
                    continue
                sinfo = None
                if stack_info:
                    sio = io.StringIO()
                    sio.write('Stack (most recent call last):\n')
                    traceback.print_stack(f, file=sio)
                    sinfo = sio.getvalue()
                    if sinfo[-1] == '\n':
                        sinfo = sinfo[:-1]
                    sio.close()
                rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
                break
            return rv


    logging.setLoggerClass(LoggerClass)


class TintFormatter(logging.Formatter):
    _instance_lock = Lock()

    def __new__(cls, *args, **kwargs):
        """利用内部锁实现的保证线程安全的单例设计模式，确保一个类只有一个实例存在"""
        if not hasattr(TintFormatter, '_instance'):
            with TintFormatter._instance_lock:
                if not hasattr(TintFormatter, '_instance'):
                    TintFormatter._instance = object.__new__(cls)
        return TintFormatter._instance

    _ansi_colors = {
        'black': 30, 'red': 31, 'green': 32, 'yellow': 33, 'blue': 34, 'magenta': 35, 'cyan': 36, 'white': 37,
        'reset': 39, 'bright_black': 90, 'bright_red': 91, 'bright_green': 92, 'bright_yellow': 93,
        'bright_blue': 94, 'bright_magenta': 95, 'bright_cyan': 96, 'bright_white': 97,
    }
    _tint_style = {
        'DEBUG': ('DEBUG', {'fg': 'bright_black'}),
        'INFO': ('INFO', {'fg': 'green'}),
        'WARNING': ('WARN', {'fg': 'yellow'}),
        'ERROR': ('ERROR', {'fg': 'red'}),
        'CRITICAL': ('FATAL', {'fg': 'red', 'bold': True}),
    }

    _full_path_mapper = {}
    _full_path_max_length = 0
    _thread_name_max_length = 0

    def __init__(self, colour: bool = False, simplify: bool = False):
        if simplify:
            super().__init__('%(datetime)s %(level)s --- %(content)s')
        else:
            super().__init__('%(datetime)s %(level)s %(pid)s --- [%(thread_name)s] %(full_path)s | %(content)s')
        self._tint = lambda text, *args, **kwargs: self._colour(text, *args, **kwargs) if colour else text
        self._simplify = simplify

    def format(self, record):
        level, color = self._tint_style.get(record.levelname)

        datetime = '{localtime}.{localtime_msecs:03.0f}'.format(
            localtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            localtime_msecs=999 if record.msecs > 999 else record.msecs
        )
        level = '{level: >5}'.format(level=level)
        content = record.getMessage()

        record.datetime = self._tint(datetime, fg='white')
        record.level = self._tint(level, **color)
        record.content = self._tint(content, **color)

        if self._simplify is False:
            pid = '{process: >5}'.format(process=record.process)
            thread_name = '{thread_name: ^{length:1}}'.format(
                thread_name=record.threadName,
                length=self._thread_name_max_length
            )
            full_path = self._format_path(record.pathname, record.lineno)

            record.pid = self._tint(pid, fg='bright_magenta')
            record.thread_name = self._tint(thread_name, fg='white', bold=True)
            record.full_path = self._tint(full_path, fg='cyan')

            if len(thread_name) > self._thread_name_max_length:
                self._thread_name_max_length = len(thread_name)
            if len(full_path) > self._full_path_max_length:
                self._full_path_mapper.clear()
                self._full_path_max_length = len(full_path)

        if record.exc_info:
            exc_info = self.formatException(record.exc_info)
            record.exc_text = self._tint(exc_info, fg='red')

        return super().format(record)

    def _format_path(self, pathname: str, lineno: int):
        """路径格式化函数（自动缩短）"""
        key = (pathname, lineno)
        if key not in self._full_path_mapper.keys():
            path_array = os.path.abspath(pathname).split(os.path.sep)
            path_array[-1] += ':{}'.format(lineno)
            while len(os.path.sep.join(path_array)) > self._full_path_max_length:
                for i in range(1, len(path_array) - 1):
                    if len(path_array[i]) > 1 and not path_array[i].endswith('..'):
                        path_array[i] = '{}..'.format(path_array[i][:1])
                        break
                else:
                    break
            self._full_path_mapper[key] = '{0: <{1}}'.format(os.path.sep.join(path_array), self._full_path_max_length)
        return self._full_path_mapper[key]

    def _colour(self, text,
                *, fg=None, bg=None, bold=None, dim=None, underline=None, blink=None, reverse=None, reset=True):
        """着色函数"""
        bits = []
        if fg:
            bits.append('\033[{}m'.format(self._ansi_colors.get(fg, 30)))
        if bg:
            bits.append('\033[{}m'.format(self._ansi_colors.get(fg, 30) + 10))
        if bold is not None:
            bits.append('\033[{}m'.format(1 if bold else 22))
        if dim is not None:
            bits.append('\033[{}m'.format(2 if dim else 22))
        if underline is not None:
            bits.append('\033[{}m'.format(4 if underline else 24))
        if blink is not None:
            bits.append('\033[{}m'.format(5 if blink else 25))
        if reverse is not None:
            bits.append('\033[{}m'.format(7 if reverse else 27))
        bits.append(text)
        if reset:
            bits.append('\033[0m')
        return ''.join(bits)


class Logger:
    def __init__(
            self, name: str = 'root', level: int = INFO, simplify: bool = True,
            *,
            console: bool = True, color: bool = True, file: Union[bool, str] = False,
            file_encoding: str = 'utf-8', file_max_bytes: int = 0, file_backup_count: int = 0
    ):
        # 初始化日志对象并日志输出等级
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)

        if console and not any(isinstance(handler, logging.StreamHandler) for handler in self._logger.handlers):
            # 配置日志输出到标准输出流
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(TintFormatter(color, simplify))
            self._logger.addHandler(hdlr=console_handler)

        if file and not any(isinstance(handler, logging.FileHandler) for handler in self._logger.handlers):
            # 配置日志输出到文件
            if isinstance(file, str):
                filename = file
            else:
                filename = '{} {}.log'.format(time.strftime('%Y%m%d_%H%M%S', time.localtime()), name)
            file_handler = RotatingFileHandler(
                filename, encoding=file_encoding, maxBytes=file_max_bytes, backupCount=file_backup_count)
            file_handler.setFormatter(TintFormatter(False, simplify))
            self._logger.addHandler(hdlr=file_handler)

    @property
    def logger(self):
        return self._logger

    def debug(self, msg, *args, stacklevel: int = 2, **kwargs) -> Optional[callable]:
        if traceback.extract_stack()[-2][3].startswith('@') or (args and isfunction(args[-1])):
            function = None
            if args and isfunction(args[-1]):
                *args, function = args
            if function is None:
                return partial(self.debug, msg, *args, **kwargs)

            @wraps(function)
            def wrapped(*func_args, **func_kwargs):
                self._logger.debug(msg, *args, stacklevel=stacklevel, **kwargs)
                return function(*func_args, **func_kwargs)

            return wrapped
        else:
            self._logger.debug(msg, *args, stacklevel=stacklevel, **kwargs)

    def info(self, msg, *args, stacklevel: int = 2, **kwargs) -> Optional[callable]:
        if traceback.extract_stack()[-2][3].startswith('@') or (args and isfunction(args[-1])):
            function = None
            if args and isfunction(args[-1]):
                *args, function = args
            if function is None:
                return partial(self.info, msg, *args, **kwargs)

            @wraps(function)
            def wrapped(*func_args, **func_kwargs):
                self._logger.info(msg, *args, stacklevel=stacklevel, **kwargs)
                return function(*func_args, **func_kwargs)

            return wrapped
        else:
            self._logger.info(msg, *args, stacklevel=stacklevel, **kwargs)

    def warning(self, msg, *args, stacklevel: int = 2, **kwargs) -> Optional[callable]:
        if traceback.extract_stack()[-2][3].startswith('@') or (args and isfunction(args[-1])):
            function = None
            if args and isfunction(args[-1]):
                *args, function = args
            if function is None:
                return partial(self.warning, msg, *args, **kwargs)

            @wraps(function)
            def wrapped(*func_args, **func_kwargs):
                self._logger.warning(msg, *args, stacklevel=stacklevel, **kwargs)
                return function(*func_args, **func_kwargs)

            return wrapped
        else:
            self._logger.warning(msg, *args, stacklevel=stacklevel, **kwargs)

    def error(self, msg, *args, stacklevel: int = 2, **kwargs) -> Optional[callable]:
        if traceback.extract_stack()[-2][3].startswith('@') or (args and isfunction(args[-1])):
            function = None
            if args and isfunction(args[-1]):
                *args, function = args
            if function is None:
                return partial(self.error, msg, *args, **kwargs)

            @wraps(function)
            def wrapped(*func_args, **func_kwargs):
                self._logger.error(msg, *args, stacklevel=stacklevel, **kwargs)
                return function(*func_args, **func_kwargs)

            return wrapped
        else:
            self._logger.error(msg, *args, stacklevel=stacklevel, **kwargs)

    def exception(self, msg, *args, exc_info=True, stacklevel: int = 2, **kwargs):
        self._logger.error(msg, *args, exc_info=exc_info, stacklevel=stacklevel, **kwargs)

    def critical(self, msg, *args, stacklevel: int = 2, **kwargs):
        self._logger.critical(msg, *args, stacklevel=stacklevel, **kwargs)

    warn = warning
    fatal = critical


__all__ = ['Logger', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'WARN', 'FATAL']
