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
@Version     : 1.0
"""
from basic import Logger, DEBUG

logger = Logger('test_logger', level=DEBUG, simplify=False)


@logger.debug('（调试）LOGGER DEBUG - DECORATOR')
def test_debug():
    pass


@logger.info('（信息）LOGGER INFO - DECORATOR')
def test_info():
    pass


@logger.warning('（警告）LOGGER WARNING - DECORATOR')
def test_warning():
    pass


@logger.error('（错误）LOGGER ERROR - DECORATOR')
def test_error():
    pass


def main():
    try:
        logger.debug('（调试）LOGGER DEBUG')
        logger.info('（信息）LOGGER INFO')
        logger.warning('（警告）LOGGER WARNING')
        logger.error('（错误）LOGGER ERROR')
        raise RuntimeError
    except RuntimeError:
        logger.exception('（异常）LOGGER EXCEPTION')
        logger.critical('（致命）LOGGER CRITICAL')

    test_debug()
    test_info()
    test_warning()
    test_error()


if __name__ == '__main__':
    main()
