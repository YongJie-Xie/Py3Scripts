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
@Version     : 1.1
"""
import logging
import os
import sys
import threading
import time
from functools import wraps, partial
from inspect import isfunction
from typing import Union

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

_default = {
    'name': 'root',
    'level': INFO,
    'simplify': True,
    'console': True,
    'color': True,
    'file': False,
}

if sys.version_info < (3, 8):
    import io
    import sys
    import traceback


    class LoggerUpdated(logging.Logger):
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


    logging.setLoggerClass(LoggerUpdated)


class Logger:
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """利用内部锁实现的保证线程安全的单例设计模式，确保一个类只有一个实例存在"""
        if not hasattr(Logger, '_instance'):
            with Logger._instance_lock:
                if not hasattr(Logger, '_instance'):
                    Logger._instance = object.__new__(cls)
        return Logger._instance

    def __init__(self, name: str = 'root', level=None, simplify=True,
                 *, console: bool = True, color: bool = True, file: Union[bool, str] = False):
        # 初始化日志对象并日志输出等级
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO if level is None else level)

        if console and not any(isinstance(handler, logging.StreamHandler) for handler in self.logger.handlers):
            # 配置日志输出到标准输出流
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(self.TintFormatter(color, simplify))
            self.logger.addHandler(hdlr=console_handler)

        if file and not any(isinstance(handler, logging.FileHandler) for handler in self.logger.handlers):
            # 配置日志输出到文件
            file_name = '{}-{}.log'.format(time.strftime('%Y%m%d%H%M%S', time.localtime()), name)
            file_handler = logging.FileHandler(file if isinstance(file, str) else file_name, encoding='utf-8')
            file_handler.setFormatter(self.TintFormatter(False, simplify))
            self.logger.addHandler(hdlr=file_handler)

    def set_level(self, level):
        self.logger.setLevel(level)

    class TintFormatter(logging.Formatter):
        _ansi_colors = {
            'black': 30, 'red': 31, 'green': 32, 'yellow': 33, 'blue': 34, 'magenta': 35, 'cyan': 36, 'white': 37,
            'reset': 39, 'bright_black': 90, 'bright_red': 91, 'bright_green': 92, 'bright_yellow': 93,
            'bright_blue': 94, 'bright_magenta': 95, 'bright_cyan': 96, 'bright_white': 97,
        }
        _thread_name_length = 0
        _full_path_length = 0

        def __init__(self, colour=False, simplify=False):
            if simplify:
                super().__init__('%(datetime)s %(level)s --- %(content)s')
            else:
                super().__init__('%(datetime)s %(level)s %(pid)s --- [%(thread_name)s] %(full_path)s | %(content)s')
            self._tint = lambda text, *args, **kwargs: self._colour(text, *args, **kwargs) if colour else text
            self._tint_dict = {}
            self._tint_style = {
                'DEBUG': ('DEBUG', {'fg': 'bright_black'}),
                'INFO': ('INFO', {'fg': 'green'}),
                'WARNING': ('WARN', {'fg': 'yellow'}),
                'ERROR': ('ERROR', {'fg': 'red'}),
                'CRITICAL': ('FATAL', {'fg': 'red', 'bold': True}),
            }
            self._simplify = simplify

        def format(self, record):
            """
            # print('{: <24}{} <--> {}'.format('record.args', record.args, '传入参数'))
            # print('{: <24}{} <--> {}'.format('record.created', record.created, '创建时间'))
            # print('{: <24}{} <--> {}'.format('record.exc_info', record.exc_info, '异常信息'))
            # print('{: <24}{} <--> {}'.format('record.exc_text', record.exc_text, ''))
            # print('{: <24}{} <--> {}'.format('record.filename', record.filename, '文件名'))
            # print('{: <24}{} <--> {}'.format('record.funcName', record.funcName, '来源函数名'))
            # print('{: <24}{} <--> {}'.format('record.getMessage()', record.getMessage(), '日志内容'))
            # print('{: <24}{} <--> {}'.format('record.levelname', record.levelname, '日志级别名称'))
            # print('{: <24}{} <--> {}'.format('record.levelno', record.levelno, '日志级别数字'))
            # print('{: <24}{} <--> {}'.format('record.lineno', record.lineno, '来源行号'))
            # print('{: <24}{} <--> {}'.format('record.module', record.module, ''))
            # print('{: <24}{} <--> {}'.format('record.msecs', record.msecs, ''))
            # print('{: <24}{} <--> {}'.format('record.msg', record.msg, '日志内容'))
            # print('{: <24}{} <--> {}'.format('record.name', record.name, '日志对象名称'))
            # print('{: <24}{} <--> {}'.format('record.pathname', record.pathname, '完整路径'))
            # print('{: <24}{} <--> {}'.format('record.process', record.process, '进程ID'))
            # print('{: <24}{} <--> {}'.format('record.processName', record.processName, '进程名称'))
            # print('{: <24}{} <--> {}'.format('record.relativeCreated', record.relativeCreated, ''))
            # print('{: <24}{} <--> {}'.format('record.stack_info', record.stack_info, ''))
            # print('{: <24}{} <--> {}'.format('record.thread', record.thread, '线程ID'))
            # print('{: <24}{} <--> {}'.format('record.threadName', record.threadName, '线程名称'))
            """
            level, color = self._tint_style.get(record.levelname)

            datetime = '{localtime}.{msecs:03.0f}'.format(
                localtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                msecs=999 if record.msecs > 999 else record.msecs)
            level = '{: >5}'.format(level)
            content = record.getMessage()

            record.datetime = self._tint(datetime, fg='white')
            record.level = self._tint(level, **color)
            record.content = self._tint(content, **color)

            if self._simplify is False:
                pid = '{: >5}'.format(record.process)
                thread_name = '{0: ^{1}}'.format(record.threadName, self._thread_name_length)
                full_path = self._format_path(record.pathname, record.lineno)

                record.pid = self._tint(pid, fg='bright_magenta')
                record.thread_name = self._tint(thread_name, fg='white', bold=True)
                record.full_path = self._tint(full_path, fg='cyan')

                if len(thread_name) > self._thread_name_length:
                    self._thread_name_length = len(thread_name)
                if len(full_path) > self._full_path_length:
                    self._full_path_length = len(full_path)

            if record.exc_info:
                exc_info = self.formatException(record.exc_info)
                record.exc_text = self._tint(exc_info, fg='red')

            return super().format(record)

        def _format_path(self, pathname: str, lineno: int):
            """路径格式化函数（自动缩短）"""
            key = (pathname, lineno)
            if key not in self._tint_dict.keys():
                path_array = os.path.abspath(pathname).split(os.path.sep)
                path_array[-1] += ':{}'.format(lineno)
                while len(os.path.sep.join(path_array)) > self._full_path_length:
                    for i in range(1, len(path_array) - 1):
                        if len(path_array[i]) > 1 and not path_array[i].endswith('..'):
                            path_array[i] = '{}..'.format(path_array[i][:1])
                            break
                    else:
                        break
                self._tint_dict[key] = '{0: <{1}}'.format(os.path.sep.join(path_array), self._full_path_length)
            return self._tint_dict[key]

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

    @classmethod
    def catch_exception(cls, *args, **kwargs):
        function = None
        if args and isfunction(args[-1]):
            *args, function = args
        if function is None:
            return partial(cls.catch_exception, *args, **kwargs)

        @wraps(function)
        def wrapped(*func_args, **func_kwargs):
            # noinspection PyBroadException
            try:
                function(*func_args, **func_kwargs)
            except Exception:
                msg, *func_args = func_args
                print(msg % func_args if func_args else msg)

        return wrapped

    @catch_exception.__get__(..., ...)
    def debug(self, msg, *args, stacklevel=3, **kwargs):
        self.logger.debug(msg, *args, stacklevel=stacklevel, **kwargs)

    @catch_exception.__get__(..., ...)
    def info(self, msg, *args, stacklevel=3, **kwargs):
        self.logger.info(msg, *args, stacklevel=stacklevel, **kwargs)

    @catch_exception.__get__(..., ...)
    def warning(self, msg, *args, stacklevel=3, **kwargs):
        self.logger.warning(msg, *args, stacklevel=stacklevel, **kwargs)

    @catch_exception.__get__(..., ...)
    def error(self, msg, *args, stacklevel=3, **kwargs):
        self.logger.error(msg, *args, stacklevel=stacklevel, **kwargs)

    @catch_exception.__get__(..., ...)
    def exception(self, msg, *args, exc_info=True, stacklevel=3, **kwargs):
        self.logger.error(msg, *args, exc_info=exc_info, stacklevel=stacklevel, **kwargs)

    @catch_exception.__get__(..., ...)
    def critical(self, msg, *args, stacklevel=3, **kwargs):
        self.logger.critical(msg, *args, stacklevel=stacklevel, **kwargs)


class Log:
    _logger = Logger(**_default)

    @classmethod
    def debug(cls, *args, **kwargs):
        function = None
        if args and isfunction(args[-1]):
            *args, function = args
        if function is None:
            return partial(cls.debug, *args, **kwargs)

        @wraps(function)
        def wrapped(*func_args, **func_kwargs):
            cls._logger.debug(*args, stacklevel=4, **kwargs)
            return function(*func_args, **func_kwargs)

        return wrapped

    @classmethod
    def info(cls, *args, **kwargs):
        function = None
        if args and isfunction(args[-1]):
            *args, function = args
        if function is None:
            return partial(cls.info, *args, **kwargs)

        @wraps(function)
        def wrapped(*func_args, **func_kwargs):
            cls._logger.info(*args, stacklevel=4, **kwargs)
            return function(*func_args, **func_kwargs)

        return wrapped

    @classmethod
    def warning(cls, *args, **kwargs):
        function = None
        if args and isfunction(args[-1]):
            *args, function = args
        if function is None:
            return partial(cls.warning, *args, **kwargs)

        @wraps(function)
        def wrapped(*func_args, **func_kwargs):
            cls._logger.warning(*args, stacklevel=4, **kwargs)
            return function(*func_args, **func_kwargs)

        return wrapped

    @classmethod
    def error(cls, *args, **kwargs):
        function = None
        if args and isfunction(args[-1]):
            *args, function = args
        if function is None:
            return partial(cls.error, *args, **kwargs)

        @wraps(function)
        def wrapped(*func_args, **func_kwargs):
            cls._logger.error(*args, stacklevel=4, **kwargs)
            return function(*func_args, **func_kwargs)

        return wrapped


logger = Logger(**_default)
log = Log()

__all__ = [
    'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL',
    'Logger', 'Log', 'logger', 'log'
]
