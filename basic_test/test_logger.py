#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author      : YongJie-Xie
@Contact     : fsswxyj@qq.com
@DateTime    : 0000-00-00 00:00
@Description : 日志操作类的测试类
@FileName    : test_logger.py
@License     : MIT License
@ProjectName : Py3Scripts
@Software    : PyCharm
@Version     : 1.2
"""
from basic import Logger, DEBUG

logger = Logger('test_logger', level=DEBUG, simplify=False)
simplify_path_logger = Logger('test_simplify_path_logger', level=DEBUG, simplify=False, simplify_path=True)
simplify_logger = Logger('test_simplify_logger', level=DEBUG, simplify=True)


@simplify_logger.info('===============================================================================================')
@simplify_logger.debug('（调试）装饰器调用 - simplify_logger.debug')
def test_debug():
    simplify_logger.debug('（调试）函数调用 - simplify_logger.debug')
    simplify_path_logger.debug('（调试）函数调用 - simplify_path_logger.debug')
    logger.debug('（调试）函数调用 - logger.debug')


@simplify_logger.info('===============================================================================================')
@simplify_logger.info('（信息）装饰器调用 - simplify_logger.info')
def test_info():
    simplify_logger.info('（信息）函数调用 - simplify_logger.info')
    simplify_path_logger.info('（调试）函数调用 - simplify_path_logger.info')
    logger.info('（信息）函数调用 - logger.info')


@simplify_logger.info('===============================================================================================')
@simplify_logger.warning('（警告）装饰器调用 - simplify_logger.warning')
def test_warning():
    simplify_logger.warning('（警告）函数调用 - simplify_logger.warning')
    simplify_path_logger.warning('（警告）函数调用 - simplify_path_logger.warning')
    logger.warning('（警告）函数调用 - logger.warning')


@simplify_logger.info('===============================================================================================')
@simplify_logger.warn('（警告）装饰器调用 - simplify_logger.warn')
def test_warn():
    simplify_logger.warn('（警告）函数调用 - simplify_logger.warn')
    simplify_path_logger.warn('（警告）函数调用 - simplify_path_logger.warn')
    logger.warn('（警告）函数调用 - logger.warn')


@simplify_logger.info('===============================================================================================')
@simplify_logger.error('（错误）装饰器调用 - simplify_logger.error')
def test_error():
    simplify_logger.error('（错误）函数调用 - simplify_logger.error')
    simplify_path_logger.error('（错误）函数调用 - simplify_path_logger.error')
    logger.error('（错误）函数调用 - logger.error')


@simplify_logger.info('===============================================================================================')
def test_exception():
    try:
        raise RuntimeError
    except RuntimeError:
        simplify_logger.exception('（异常）函数调用 - simplify_logger.exception')
        simplify_path_logger.exception('（异常）函数调用 - simplify_path_logger.exception')
        logger.exception('（异常）函数调用 - logger.exception')


@simplify_logger.info('===============================================================================================')
def test_critical():
    simplify_logger.critical('（致命）函数调用 - simplify_logger.critical')
    simplify_path_logger.critical('（致命）函数调用 - simplify_path_logger.critical')
    logger.critical('（致命）函数调用 - logger.critical')


@simplify_logger.info('===============================================================================================')
def test_fatal():
    simplify_logger.fatal('（致命）函数调用 - simplify_logger.fatal')
    simplify_path_logger.fatal('（致命）函数调用 - simplify_path_logger.fatal')
    logger.fatal('（致命）函数调用 - logger.fatal')


def main():
    test_debug()
    test_info()
    test_warning()
    test_warn()
    test_error()
    test_exception()
    test_critical()
    test_fatal()


if __name__ == '__main__':
    main()
