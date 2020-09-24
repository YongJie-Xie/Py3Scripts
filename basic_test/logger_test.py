#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author      : YongJie-Xie
@Contact     : fsswxyj@qq.com
@DateTime    : 0000-00-00 00:00
@Description : 日志操作类的测试类
@FileName    : logger_test.py
@License     : MIT License
@ProjectName : Py3Scripts
@Software    : PyCharm
@Version     : 1.0
"""
from basic import DEBUG, logger, log


@log.debug('（调试）DECORATOR LOGGER DEBUG')
@log.info('（信息）DECORATOR LOGGER INFO')
@log.warning('（警告）DECORATOR LOGGER WARNING')
@log.error('（错误）DECORATOR LOGGER ERROR')
def main():
    logger.debug('（调试）LOGGER DEBUG')
    logger.info('（信息）LOGGER INFO')
    logger.warning('（警告）LOGGER WARNING')
    logger.error('（错误）LOGGER ERROR')
    try:
        raise RuntimeError
    except RuntimeError:
        logger.exception('（异常）LOGGER EXCEPTION')
    logger.critical('（致命）LOGGER CRITICAL')


if __name__ == '__main__':
    logger.set_level(DEBUG)
    main()
