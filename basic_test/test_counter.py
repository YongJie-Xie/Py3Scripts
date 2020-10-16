#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author      : YongJie-Xie
@Contact     : fsswxyj@qq.com
@DateTime    : 0000-00-00 00:00
@Description : ''
@FileName    : test_counter.py
@License     : MIT License
@ProjectName : Py3Scripts
@Software    : PyCharm
@Version     : 1.0
"""
from basic import Logger, Counter

logger = Logger('test_counter')


def main():
    counter = Counter(default=99)
    logger.info('counter.count default: %s', counter)
    counter.count += 99
    logger.info('counter.count += 99: %s', counter.count)
    counter.add(99)
    logger.info('counter.add(99): %s', str(counter))


if __name__ == '__main__':
    main()
